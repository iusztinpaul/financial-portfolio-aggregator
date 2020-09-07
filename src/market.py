import datetime
import json
import concurrent.futures

from collections import OrderedDict
from pathlib import Path
from typing import Optional, List

import pandas
import tqdm
import yfinance

from pandas_datareader.nasdaq_trader import get_nasdaq_symbols

from src import settings
from src.models import Holding


class Market:
    market: 'Market' = None

    def __init__(self, market_name: str, expire_after_days: datetime.timedelta):
        self.market_name = market_name
        self.expire_after_days = expire_after_days

        self.market_meta_file = Path(settings.STORAGE_PATH) / 'market_metadata.json'
        self.holdings_file = Path(settings.STORAGE_PATH) / f'{self.market_name}_holdings.csv'
        self.missed_holdings = -1  # Parameter to describe the number of faulty requests for a holding.

        if self.should_refresh_data():
            holdings = self.get_data_from_cloud()
            self.save_data_to_disk(holdings)
            self.save_update_datetime()
        else:
            holdings = self.get_data_from_disk()

        self.holdings = self.populate(holdings)

    def get_data_from_cloud(self) -> List[Holding]:
        raise NotImplementedError()

    def save_data_to_disk(self, holdings: List[Holding]):
        print(f'Saving data to disk for: {self.market_name}')

        with open(str(self.holdings_file), 'w') as f:
            f.write('Name,Ticker,Country,Currency,Exchange\n')
            for holding in tqdm.tqdm(holdings):
                f.write(
                    f'{holding.normalized_name},'
                    f'{holding.ticker},'
                    f'{holding.country},'
                    f'{holding.currency},'
                    f'{holding.exchange}\n'
                )

    def get_data_from_disk(self) -> List[Holding]:
        print(f'Getting data from disk for: {self.market_name}')

        holdings = []
        holdings_dataframe = pandas.read_csv(self.holdings_file)
        for _, holding_dataframe in holdings_dataframe.iterrows():
            holding = Holding(
                name=holding_dataframe['Name'],
                ticker=holding_dataframe['Ticker'],
                country=holding_dataframe['Country'],
                currency=holding_dataframe['Currency'],
                exchange=holding_dataframe['Exchange']
            )

            holdings.append(holding)

        return holdings

    def populate(self, holdings: List[Holding]) -> OrderedDict:
        return OrderedDict({
            h: h for h in holdings
        })

    def should_refresh_data(self):
        last_update_date_time = self.get_last_update_datetime()
        if last_update_date_time is None:
            return True

        now = datetime.datetime.utcnow()

        return now - self.expire_after_days > last_update_date_time

    def get_last_update_datetime(self) -> Optional[datetime.datetime]:
        if not self.market_meta_file.exists():
            return None

        with open(str(self.market_meta_file), 'r') as f:
            market_metadata = json.load(f)

        specific_market_metadata = market_metadata.get(self.market_name, dict())
        timestamp = specific_market_metadata.get('timestamp')
        if timestamp is None:
            return None

        return datetime.datetime.utcfromtimestamp(timestamp)

    def save_update_datetime(self):
        update_datetime = datetime.datetime.utcnow()
        update_timestamp = update_datetime.timestamp()

        if self.market_meta_file.exists():
            with open(str(self.market_meta_file), 'r') as f:
                market_metadata = json.load(f)

            specific_market_metadata = market_metadata.get(self.market_name, dict())
            specific_market_metadata.update({
                'timestamp': update_timestamp
            })
            market_metadata[self.market_name] = specific_market_metadata
        else:
            market_metadata = {
                self.market_name: {
                    'timestamp': update_timestamp
                }
            }

        with open(str(self.market_meta_file), 'w') as f:
            json.dump(market_metadata, f)

    def query(self, holding: Holding) -> Optional[Holding]:
        return self.holdings.get(holding)


class NasdaqMarket(Market):
    def __init__(self, expire_after_days: datetime.timedelta):
        super().__init__('Nasdaq', expire_after_days)

    def get_data_from_cloud(self) -> List[Holding]:
        symbols = get_nasdaq_symbols()
        tickers = [ticker for ticker in symbols['NASDAQ Symbol']]

        holdings = []
        self.missed_holdings = 0

        print(f'Getting data from cloud for: {self.market_name}')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for ticker in tickers:
                futures.append(
                    executor.submit(
                        self._get_holding_from_cloud, ticker=ticker
                    )
                )

            for future in concurrent.futures.as_completed(futures):

                try:
                    holding = future.result()

                    if holding is not None:
                        holdings.append(holding)
                except (ConnectionError, TimeoutError):
                    self.missed_holdings += 1

        return holdings

    def _get_holding_from_cloud(self, ticker: str) -> Optional[Holding]:
        print(f'Get holding from cloud: {ticker}')

        company = yfinance.Ticker(ticker)
        name = \
            company.info.get('shortName') or \
            company.info.get('longName') or \
            company.info.get('displayName') or \
            company.info.get('fullExchangeName')

        if name is None:
            return None

        holding = Holding(
            name=name,
            ticker=ticker,
            country=company.info.get('region'),
            currency=company.info.get('financialCurrency'),
            exchange=company.info.get('fullExchangeName')
        )

        return holding


class MarketHub:
    EXPIRE_AFTER_DAYS = datetime.timedelta(days=31)
    market_hub: 'MarketHub' = None

    # TODO: Make this class truly singletone
    def __init__(self):
        self.markets = [
            NasdaqMarket(self.EXPIRE_AFTER_DAYS)
        ]

    @classmethod
    def get(cls):
        if cls.market_hub is None:
            cls.market_hub = MarketHub()

        return cls.market_hub

    def query(self, holding: Holding) -> Optional[Holding]:
        for market in self.markets:
            queried_holding = holding = market.query(holding)
            if queried_holding:
                return queried_holding

        return None


if __name__ == '__main__':
    market_hub = MarketHub.get()
    market_hub.query(Holding('Apple', 'AAPL'))
