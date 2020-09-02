from collections import OrderedDict
from typing import List, Tuple

import tqdm


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
        self.ticker = ticker
        self.country = country
        self.sector = sector
        self.industry = industry
        self.currency = currency
        self.exchange = exchange

    def __str__(self):
        if self.ticker:
            return f'{self.ticker}: {self.name}'

        return f'{self.name}'

    def __eq__(self, other, name_words_iou_threshold=0.75):
        if not isinstance(other, Holding):
            return False

        if other.ticker and self.ticker and other.ticker.upper() == self.ticker.upper():
            return True

        other_name_set = set(other.name.upper().split(' '))
        self_name_set = set(self.name.upper().split(' '))
        common_name_words = other_name_set.union(self_name_set)

        name_words_iou = len(common_name_words) / len(self_name_set)
        assert name_words_iou <= 1

        return name_words_iou >= name_words_iou_threshold

    def __hash__(self):
        return self.name.__hash__()


class FinancialInstrument:
    def __init__(self, name):
        self.name = name
        self.holdings = OrderedDict()

    def add_holding_weight(self, holding: Holding, weight: float):
        assert weight <= 1

        self.holdings[holding] = self.get_holding_weight(holding) + weight

    def get_holding_weight(self, holding: Holding):
        return self.holdings.get(holding, 0)

    @staticmethod
    def aggregate(etfs: List[Tuple[float, 'FinancialInstrument']]):
        aggregated_etfs = FinancialInstrument('Aggregated ETF')

        assert sum([etf[0] for etf in etfs]) == 1, 'Your etf holdings should sum up to 1.'

        for etf_weight, etf in etfs:
            for holding, weight in etf.holdings.items():
                new_weight = etf_weight * weight
                aggregated_etfs.add_holding_weight(holding, new_weight)

        assert sum(aggregated_etfs.holdings.values()) > 0.99, 'Your holdings should sum up to around ~1.'

        return aggregated_etfs

    def export_to_csv(self, file_path='portfolio.csv') -> str:
        self.holdings = {k: v for k, v in sorted(self.holdings.items(), key=lambda item: -item[1])}

        print('Exporting CSV file...')
        with open(file_path, 'w') as f:
            f.write(f'Name,Ticker,Weight,Country,Sector\n')
            for holding, weight in tqdm.tqdm(self.holdings.items()):
                f.write(f'{holding.name},{holding.ticker},{weight*100},{holding.country},{holding.sector}\n')

        return file_path


class ETF(FinancialInstrument):
    pass


class OneItemInstrument(FinancialInstrument):
    pass


class Portfolio(FinancialInstrument):
    def __init__(self):
        super(Portfolio, self).__init__('Portfolio')
