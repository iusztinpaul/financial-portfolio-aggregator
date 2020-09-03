from collections import OrderedDict
from typing import List, Tuple

import tqdm

from src.utils import normalize_name, normalize_country


class Holding:
    def __init__(
            self,
            name,
            ticker=None,
            country=None,
            sector=None,
            industry=None,
            currency=None,
            exchange=None
    ):
        self.name = name
        self.normalized_name = normalize_name(name)
        self.ticker = ticker
        self.country = normalize_country(country)
        self.sector = sector
        self.industry = industry
        self.currency = currency
        self.exchange = exchange

    def __str__(self):
        if self.ticker:
            return f'{self.ticker}: {self.normalized_name}'

        return f'{self.normalized_name}'

    def __eq__(self, other, name_words_iou_threshold=0.75):
        if not isinstance(other, Holding):
            return False

        if other.ticker and self.ticker and other.ticker.upper() == self.ticker.upper():
            return True

        if other.first_normalized_name_word() != self.first_normalized_name_word():
            return False

        other_name_set = set(other.normalized_name.split(' '))
        self_name_set = set(self.normalized_name.split(' '))
        common_name_words = other_name_set.intersection(self_name_set)

        name_words_iou = len(common_name_words) / len(self_name_set)
        assert name_words_iou <= 1

        return name_words_iou > name_words_iou_threshold

    def first_normalized_name_word(self):
        return self.normalized_name.split(' ')[0]

    @classmethod
    def aggregate(cls, holding_1, holding_2):
        def aggregate_attribute(h1, h2, attribute: str):
            return getattr(h1, attribute) or getattr(h2, attribute)

        holding_1.ticker = aggregate_attribute(holding_1, holding_2, 'ticker')
        holding_1.country = aggregate_attribute(holding_1, holding_2, 'country')
        holding_1.sector = aggregate_attribute(holding_1, holding_2, 'sector')
        holding_1.industry = aggregate_attribute(holding_1, holding_2, 'industry')
        holding_1.currency = aggregate_attribute(holding_1, holding_2, 'currency')
        holding_1.exchange = aggregate_attribute(holding_1, holding_2, 'exchange')

        return holding_1

    def __hash__(self):
        return self.normalized_name.split(' ')[0].__hash__()


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
    def __init__(self, name):
        super().__init__(name)

        holding = Holding(name)
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
    def __init__(self, name):
        super().__init__(name)
        self.holdings = OrderedDict()

    def add_holding_weight(self, holding: Holding, weight: float):
        assert weight <= 1

        old_weight = self.get_holding_weight(holding)
        old_holding = self.get_holding(holding.name, holding.ticker)
        if old_holding:
            holding = Holding.aggregate(holding, old_holding)

        self.holdings[holding] = {
            'weight': old_weight + weight,
            'holding': holding
        }

    def get_holding_weight(self, holding: Holding) -> float:
        return self.holdings.get(holding, {'weight': 0.})['weight']

    def get_holding(self, name, ticker=None) -> Holding:
        holding = Holding(name, ticker=ticker)

        return self.holdings.get(holding, {'holding': None})['holding']

    @staticmethod
    def aggregate(etfs: List[Tuple[float, FinancialInstrument]]):
        aggregated_etfs = MultipleItemsFinancialInstrument('Aggregated ETF')

        assert sum([etf[0] for etf in etfs]) == 1, 'Your etf holdings should sum up to 1.'

        print('Aggregating financial instruments...')
        for etf_weight, etf in tqdm.tqdm(etfs):
            for holding, weight in etf.get_values():
                new_weight = etf_weight * weight
                aggregated_etfs.add_holding_weight(holding, new_weight)

        aggregated_etfs.assert_holdings_summed_value()
        aggregated_etfs.sort_holdings()

        return aggregated_etfs

    def sort_holdings(self):
        self.holdings = {k: v for k, v in sorted(self.holdings.items(), key=lambda item: -item[1]['weight'])}

    def assert_holdings_summed_value(self):
        assert sum(self.get_weights()) > 0.985, 'Your holdings should sum up to around ~1.'

    def export_to_csv(self, file_path='portfolio.csv') -> str:
        self.sort_holdings()

        print('Exporting CSV file...')
        with open(file_path, 'w') as f:
            f.write(f'Name,Ticker,Weight,Country,Sector\n')
            for holding, weight in tqdm.tqdm(self.get_values()):
                f.write(f'{holding.normalized_name},{holding.ticker},{weight*100},{holding.country},{holding.sector}\n')

        return file_path

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
            print(f'\t{item}: {value*100}%')


class ETF(MultipleItemsFinancialInstrument):
    pass


class Portfolio(MultipleItemsFinancialInstrument):
    def __init__(self):
        super(Portfolio, self).__init__('Portfolio')
