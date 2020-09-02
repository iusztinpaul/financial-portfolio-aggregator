from src.factories import create_etf_from_ishares_csv, create_etf_from_spdr_excel, create_etf_from_vanguard, \
    create_etf_from_custom_csv
from src.models import MultipleItemsFinancialInstrument, OneItemFinancialInstrument

# TODO: Change holding aggregation algorithm, make the dictionary like: [holding] = { 'weight', 'holding' }
# TODO: Validate weight calculating logic.
# TODO: Create statistics by region & sector.
# TODO: Add docs.
# TODO: Add args for more generic purposes.


if __name__ == '__main__':
    cndx_etf = create_etf_from_ishares_csv(
        'CNDX',
        'files/CNDX_holdings.csv'
    )
    spym_etf = create_etf_from_spdr_excel(
        'CNDX',
        'files/holdings-daily-emea-en-spym-gy.xlsx'
    )
    vusd_etf = create_etf_from_vanguard(
        'VUSD',
        'files/HoldingDetails_S&P_500_UCITS_ETF_-_(USD)_Distributing_(VUSD).csv'
    )
    vdev_etf = create_etf_from_vanguard(
        'VDEV',
        'files/HoldingDetails_FTSE_Developed_World_UCITS_ETF_-_(USD)_Distributing_(VDEV).csv'
    )

    etf_portfolio = MultipleItemsFinancialInstrument.aggregate(
        [
            (0.4, vusd_etf),
            (0.2, cndx_etf),
            (0.2, vdev_etf),
            (0.2, spym_etf)
        ]
    )
    stocks_portfolio = create_etf_from_custom_csv(
        'Stocks',
        'files/Portfolio - Stocks.csv'
    )
    cash = OneItemFinancialInstrument('Cash')
    mutual_fund = OneItemFinancialInstrument('Mutual Fund')
    bonds = OneItemFinancialInstrument('Bonds')
    bitcoin = OneItemFinancialInstrument('Bitcoin')
    gold = OneItemFinancialInstrument('Gold')

    portfolio = MultipleItemsFinancialInstrument.aggregate(
        [
            (0.50, etf_portfolio),
            (0.30, cash),
            (0.10, stocks_portfolio),
            (0.06, bonds),
            (0.03, mutual_fund),
            (0.005, bitcoin),
            (0.005, gold),
        ]
    )
    portfolio.export_to_csv()
