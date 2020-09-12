from collections import OrderedDict
from typing import List, Tuple, Union, Optional

import tqdm

from src.choices import HoldingTypeChoices
from src.network.managers import GoogleSheetsManager
from src.normalizers.attribute import HoldingAttributesNormalizer
from src.settings import SPREAD_SHEET_ID


class Holding:
    normalizer = HoldingAttributesNormalizer()

    def __init__(
            self,
            name,
            ticker=None,
            country=None,
            sector=None,
            industry=None,
            currency=None,
            exchange=None,
            holding_type: str = None
    ):
        self.name = name
        self.normalized_name = self.normalizer.normalize_name(name)
        self.ticker = ticker
        self.country = self.normalizer.normalize_country(country)
        self.sector = sector
        self.industry = industry
        self.currency = currency
        self.exchange = exchange
        self.holding_type = self.normalizer.normalize_type(holding_type)

    @property
    def is_leaf(self) -> bool:
        return self.holding_type != HoldingTypeChoices.ETF

    def __str__(self):
        if self.ticker:
            return f'{self.ticker}: {self.normalized_name}'

        return f'{self.normalized_name}'

    def __eq__(self, other, name_words_iou_threshold=0.6):
        if not isinstance(other, Holding):
            return False

        if other.ticker and self.ticker:
            return other.ticker.upper() == self.ticker.upper()

        if other.first_normalized_name_word() != self.first_normalized_name_word():
            return False

        other_name_set = set(other.normalized_name.split(' '))
        self_name_set = set(self.normalized_name.split(' '))

        intersections_name_words = other_name_set.intersection(self_name_set)
        reunion_name_words = other_name_set.union(self_name_set)
        iou = len(intersections_name_words) / len(reunion_name_words)

        assert iou <= 1.

        return iou >= name_words_iou_threshold

    def __hash__(self):
        return self.normalized_name.split(' ')[0].__hash__()

    def first_normalized_name_word(self):
        return self.normalized_name.split(' ')[0]

    @classmethod
    def aggregate(cls, holding_1, holding_2):
        def aggregate_attribute(h1, h2, attribute: str):
            return getattr(h1, attribute) or getattr(h2, attribute)

        if holding_1 is None:
            return holding_2

        if holding_2 is None:
            return holding_1

        holding_1.ticker = aggregate_attribute(holding_1, holding_2, 'ticker')
        holding_1.country = aggregate_attribute(holding_1, holding_2, 'country')
        holding_1.sector = aggregate_attribute(holding_1, holding_2, 'sector')
        holding_1.industry = aggregate_attribute(holding_1, holding_2, 'industry')
        holding_1.currency = aggregate_attribute(holding_1, holding_2, 'currency')
        holding_1.exchange = aggregate_attribute(holding_1, holding_2, 'exchange')

        return holding_1

    @classmethod
    def aggregate_with_hub(cls, holding_1, holding_2):
        from src.markets import MarketHub

        market_hub = MarketHub.get()
        holding_from_hub = market_hub.query(holding_1 or holding_2)

        holding = Holding.aggregate(holding_1, holding_2)
        holding = Holding.aggregate(holding, holding_from_hub)

        return holding

    def to_leaves(self) -> Optional['MultipleItemsFinancialInstrument']:
        from src import network
        from src import disk

        assert not self.is_leaf

        instrument = None
        instrument_source = network.get_source(self.ticker) or disk.get_source(self.ticker)

        instrument_factory = network.get_from_network(instrument_source)
        if instrument_factory:
            instrument = instrument_factory(self.ticker)

        instrument_factory = disk.get_from_disk(instrument_source)
        if instrument_factory:
            instrument = instrument_factory(self.ticker)

        if instrument is None:
            return None

        return instrument.to_leaves()



class FinancialInstrument:
    def __init__(self, name):
        self.name = name
        self.holdings = OrderedDict()

    def get_holding_weight(self, holding: Holding) -> float:
        raise NotImplementedError()

    def get_holding(self, name, ticker=None) -> Holding:
        raise NotImplementedError()

    def get_weights(self) -> List:
        return [value['weight'] for value in self.holdings.values()]

    def get_holdings(self) -> List:
        return [value['holding'] for value in self.holdings.values()]

    def get_values(self):
        return zip(self.get_holdings(), self.get_weights())


class OneItemFinancialInstrument(FinancialInstrument):
    def __init__(self, name, **kwargs):
        super().__init__(name)

        holding = Holding(name, **kwargs)
        self.holding = holding

        self.holdings[holding] = {
            'holding': holding,
            'weight': 1.
        }

    def get_holding_weight(self, holding: Holding) -> float:
        return 1.

    def get_holding(self, name, ticker=None) -> Holding:
        return self.holding


class MultipleItemsFinancialInstrument(FinancialInstrument):
    SUMMED_WEIGHTS_THRESHOLD = 0.985

    def __init__(self, name):
        super().__init__(name)
        self.holdings = OrderedDict()

    def add_holding_weight(self, holding: Holding, weight: float):
        assert weight <= 1

        old_weight = self.get_holding_weight(holding)

        old_holding = self.get_holding(holding.name, holding.ticker)
        holding = Holding.aggregate_with_hub(old_holding, holding)

        self.holdings[holding] = {
            'weight': old_weight + weight,
            'holding': holding
        }

    def get_holding_weight(self, holding: Union[Holding, str]) -> float:
        if isinstance(holding, str):
            holding = Holding(name=holding)

        return self.holdings.get(holding, {'weight': 0.})['weight']

    def get_holding(self, name, ticker=None) -> Holding:
        holding = Holding(name, ticker=ticker)

        return self.holdings.get(holding, {'holding': None})['holding']

    def to_leaves(self) -> 'MultipleItemsFinancialInstrument':
        new_instrument = MultipleItemsFinancialInstrument(self.name)

        for holding, weight in self.get_values():
            if holding.is_leaf:
                new_instrument.add_holding_weight(holding, weight)
            else:
                reduced_instrument = holding.to_leaves()

                assert reduced_instrument is not None, 'Cannot reduce instrument'

                for reduced_holding, reduced_weight in reduced_instrument.get_values():
                    new_instrument.add_holding_weight(reduced_holding, weight*reduced_weight)

        new_instrument.sort_holdings()
        new_instrument.assert_holdings_summed_value()

        return new_instrument

    @classmethod
    def aggregate(cls, financial_instruments: List[Tuple[float, FinancialInstrument]]):
        aggregated_etfs = MultipleItemsFinancialInstrument('Aggregated ETF')

        assert sum([etf[0] for etf in financial_instruments]) > cls.SUMMED_WEIGHTS_THRESHOLD, \
            'Your etf holdings should sum up to 1.'

        print('Aggregating financial instruments...')
        for financial_instrument_weight, financial_instrument in tqdm.tqdm(financial_instruments):
            for holding, weight in financial_instrument.get_values():
                new_weight = financial_instrument_weight * weight
                aggregated_etfs.add_holding_weight(holding, new_weight)

        aggregated_etfs.sort_holdings()
        aggregated_etfs.assert_holdings_summed_value()

        return aggregated_etfs

    def sort_holdings(self):
        self.holdings = OrderedDict(sorted(self.holdings.items(), key=lambda item: -item[1]['weight']))

    def assert_holdings_summed_value(self):
        assert sum(self.get_weights()) > self.SUMMED_WEIGHTS_THRESHOLD, 'Your holdings should sum up to around ~1.'

    def export_to_csv(self, file_path='portfolio.csv') -> str:
        self.sort_holdings()

        print('Exporting CSV file...')
        with open(file_path, 'w') as f:
            f.write(f'Name,Ticker,Weight,Country,Sector\n')
            for holding, weight in tqdm.tqdm(self.get_values()):
                f.write(
                    f'{holding.normalized_name},{holding.ticker},{weight * 100},{holding.country},{holding.sector}\n')

        return file_path

    def export_to_google_sheets(self, workspace_name='Aggregated'):
        """
            sheet_name: the name of your google sheets sheet
        """
        self.sort_holdings()

        print('Exporting to google sheets...')
        data = [['Name', 'Ticker', 'Weight', 'Country', 'Sector']]
        for holding, weight in tqdm.tqdm(self.get_values()):
            data.append([
                holding.normalized_name,
                holding.ticker,
                weight * 100,
                holding.country,
                holding.sector
            ])

        google_sheets_manager = GoogleSheetsManager(SPREAD_SHEET_ID)
        google_sheets_manager.write(data=data, workspace_name=workspace_name)

    def statistics_country(self):
        self.statistics('country')

    def statistics_sector(self):
        self.statistics('sector')

    def statistics(self, attribute_key: str):
        counter = OrderedDict()

        for holding_data in self.holdings.values():
            holding: Holding = holding_data['holding']
            weight: float = holding_data['weight']

            attribute_value = getattr(holding, attribute_key)

            counter[attribute_value] = counter.get(attribute_value, 0) + weight

        counter = {k: v for k, v in sorted(counter.items(), key=lambda item: -item[1])}

        total = sum(counter.values())
        assert total > 0.98

        print(f'Statistics {attribute_key}')
        for item, value in counter.items():
            print(f'\t{item}: {value * 100}%')


class ETF(MultipleItemsFinancialInstrument):
    pass


class Portfolio(MultipleItemsFinancialInstrument):
    def __init__(self):
        super(Portfolio, self).__init__('Portfolio')
