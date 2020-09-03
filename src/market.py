import datetime

import requests_cache

from collections import OrderedDict
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols


class Market:
    market: 'Market' = None

    def __init__(self, expire_after_days=7):
        self.holdings = OrderedDict()
        self.session = requests_cache.CachedSession(
            cache_name='cache',
            backend='sqlite',
            expire_after=datetime.timedelta(days=expire_after_days)
        )

        self.populate()

    def populate(self):
        raise NotImplementedError()


class NasdaqMarket(Market):
    def populate(self):
        symbols = get_nasdaq_symbols()
        with open('nasdaq_symbols.csv', 'w') as f:
            f.write(f'{",".join(symbols.columns)}\n')
            for _, symbol in symbols.iterrows():
                columns = list(symbols.columns)
                for col in columns[:-1]:
                    f.write(f'{symbol[col]},')

                f.write(f'{symbol[columns[-1]]}\n')


class MarketHub:
    market_hub: 'MarketHub' = None

    # TODO: Make this class truly singletone
    def __init__(self):
        self.markets = [
            NasdaqMarket()
        ]

    @classmethod
    def get(cls):
        if cls.market_hub is None:
            cls.market_hub = MarketHub()

        return cls.market_hub
