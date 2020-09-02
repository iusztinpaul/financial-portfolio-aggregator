from collections import OrderedDict
from typing import List, Tuple

import tqdm

from src.utils import normalize_name


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
        self.country = country
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

    def __hash__(self):
        return self.normalized_name.split(' ')[0].__hash__()


class FinancialInstrument:
    def __init__(self, name):
        self.name = name
        self.holdings = OrderedDict()

    def get_holding_weight(self, holding: Holding) -> float:
        raise NotImplementedError()


class OneItemFinancialInstrument(FinancialInstrument):
    def __init__(self, name):
        super().__init__(name)

        holding = Holding(name)
        self.holdings[holding] = 1.

    def get_holding_weight(self, holding: Holding) -> float:
        return self.holdings.get(holding, 1.)


class MultipleItemsFinancialInstrument(FinancialInstrument):
    def __init__(self, name):
        super().__init__(name)
        self.holdings = OrderedDict()

    def add_holding_weight(self, holding: Holding, weight: float):
        assert weight <= 1

        old_weight = self.get_holding_weight(holding)
        holding = self.aggregate_holdings(holding)

        self.holdings[holding] = old_weight + weight

    def get_holding_weight(self, holding: Holding) -> float:
        return self.holdings.get(holding, 0)

    def aggregate_holdings(self, new_holding):
        def aggregate_attribute(h1, h2, attribute: str):
            return getattr(h1, attribute) or getattr(h2, attribute)

        if new_holding not in self.holdings:
            return new_holding

        current_holding = None
        for holding in self.holdings.keys():
            if holding == new_holding:
                current_holding = holding
                break

        if current_holding:
            new_holding.ticker = aggregate_attribute(current_holding, new_holding, 'ticker')
            new_holding.country = aggregate_attribute(current_holding, new_holding, 'country')
            new_holding.sector = aggregate_attribute(current_holding, new_holding, 'sector')
            new_holding.industry = aggregate_attribute(current_holding, new_holding, 'industry')
            new_holding.currency = aggregate_attribute(current_holding, new_holding, 'currency')
            new_holding.exchange = aggregate_attribute(current_holding, new_holding, 'exchange')

        return new_holding

    @staticmethod
    def aggregate(etfs: List[Tuple[float, FinancialInstrument]]):
        aggregated_etfs = MultipleItemsFinancialInstrument('Aggregated ETF')

        assert sum([etf[0] for etf in etfs]) == 1, 'Your etf holdings should sum up to 1.'

        print('Aggregating financial instruments...')
        for etf_weight, etf in tqdm.tqdm(etfs):
            for holding, weight in etf.holdings.items():
                new_weight = etf_weight * weight
                aggregated_etfs.add_holding_weight(holding, new_weight)

        aggregated_etfs.assert_holdings_summed_value()
        aggregated_etfs.sort_holdings()

        return aggregated_etfs

    def sort_holdings(self):
        self.holdings = {k: v for k, v in sorted(self.holdings.items(), key=lambda item: -item[1])}

    def assert_holdings_summed_value(self):
        assert sum(self.holdings.values()) > 0.985, 'Your holdings should sum up to around ~1.'

    def export_to_csv(self, file_path='portfolio.csv') -> str:
        self.sort_holdings()

        print('Exporting CSV file...')
        with open(file_path, 'w') as f:
            f.write(f'Name,Ticker,Weight,Country,Sector\n')
            for holding, weight in tqdm.tqdm(self.holdings.items()):
                f.write(f'{holding.normalized_name},{holding.ticker},{weight*100},{holding.country},{holding.sector}\n')

        return file_path


class ETF(MultipleItemsFinancialInstrument):
    pass


class Portfolio(MultipleItemsFinancialInstrument):
    def __init__(self):
        super(Portfolio, self).__init__('Portfolio')
