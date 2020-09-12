from enum import Enum


class GoogleSheetsColumnChoices(Enum):
    NAME = 'Name'
    TICKER = 'Ticker'
    PERCENTAGE = 'Percentage'
    TYPE = 'Type'


class HoldingTypeChoices(Enum):
    CASH = 'CASH'
    ETF = 'ETF'
    STOCK = 'STOCK'
    MUTUAL_FUND = 'MUTUAL FUND'
    BOND = 'BOND'
    COMMODITY = 'COMMODITY'
