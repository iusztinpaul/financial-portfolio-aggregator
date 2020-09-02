from factories import create_etf_from_ishares_csv, create_etf_from_spdr_excel, create_etf_from_vanguard, \
    create_etf_from_custom_csv, create_one_item_instrument
from models import FinancialInstrument

# TODO: Add repo to github.
# TODO: Make a mechanism to get tickers by stock name / Create a better holding equality mechanism.
# TODO: Create statistics by region & sector.
# TODO: Validate weight calculating logic.
# TODO: Add docs.
# TODO: Add args for more generic purposes.


if __name__ == '__main__':
    cndx_etf = create_etf_from_ishares_csv(
        'CNDX',
        './files/CNDX_holdings.csv'
    )
    spym_etf = create_etf_from_spdr_excel(
        'CNDX',
        './files/holdings-daily-emea-en-spym-gy.xlsx'
    )
    vusd_etf = create_etf_from_vanguard(
        'VUSD',
        './files/HoldingDetails_S&P_500_UCITS_ETF_-_(USD)_Distributing_(VUSD).csv'
    )
    vdev_etf = create_etf_from_vanguard(
        'VDEV',
        '/home/peius/Documents/Projects/etf-aggregator/files/HoldingDetails_FTSE_Developed_World_UCITS_ETF_-_(USD)_Distributing_(VDEV).csv'
    )

    etf_portfolio = FinancialInstrument.aggregate(
        [
            (0.4, vusd_etf),
            (0.2, cndx_etf),
            (0.2, vdev_etf),
            (0.2, spym_etf)
        ]
    )
    stocks_portfolio = create_etf_from_custom_csv(
        'Stocks',
        '/home/peius/Documents/Projects/etf-aggregator/files/Portfolio - Stocks.csv'
    )
    cash = create_one_item_instrument('Cash')
    mutual_fund = create_one_item_instrument('Mutual Fund')
    bonds = create_one_item_instrument('Bonds')
    bitcoin = create_one_item_instrument('Bitcoin')
    gold = create_one_item_instrument('Gold')

    portfolio = FinancialInstrument.aggregate(
        [
            (0.45, etf_portfolio),
            (0.30, cash),
            (0.15, stocks_portfolio),
            (0.03, mutual_fund),
            (0.05, bonds),
            (0.01, bitcoin),
            (0.01, gold),
        ]
    )
    portfolio.export_to_csv()
