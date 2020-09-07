from src.factories import create_etf_from_vanguard
from src.factories.download import get_etf_ishares, get_etf_spdr
from src.models import MultipleItemsFinancialInstrument

# TODO: Hook etf calculation with google sheets ( read portfolio, write aggregated data)
# TODO: Download etfs files dinamically.
# TODO: Add docs.cn
# TODO: Add args for more generic purposes.
# TODO: Add env support for settings
# TODO: Add financial data support.
# TODO: Make a better sector & industry normalization.
# TODO: Improve your model __eq__ method && name_normalize() function


if __name__ == '__main__':
    cndx_etf = get_etf_ishares('CNDX')
    cspx_etf = get_etf_ishares('CSPX')
    iuit_etf = get_etf_ishares('IUIT')
    wcos_etf = get_etf_spdr('WCOS')
    vhyl_etf = create_etf_from_vanguard(
        'VHYL',
        'files/Holding_detailsHolding_details_FTSE_All-World_High_Dividend_Yield_UCITS_ETF_(USD)___Distributing_(VHYL).csv'
    )
    vfem_etf = create_etf_from_vanguard(
        'VFEM',
        'files/Holding_detailsHolding_details_FTSE_Emerging_Markets_UCITS_ETF_(USD)___Distributing_(VFEM).csv'
    )

    etf_portfolio = MultipleItemsFinancialInstrument.aggregate(
        [
            (0.45, cspx_etf),
            (0.1, cndx_etf),
            (0.1, iuit_etf),
            (0.1, wcos_etf),
            (0.15, vhyl_etf),
            (0.1, vfem_etf)
        ]
    )
    etf_portfolio.export_to_csv()
    etf_portfolio.statistics_sector()
    etf_portfolio.statistics_country()
    # stocks_portfolio = create_etf_from_custom_csv(
    #     'Stocks',
    #     'files/Portfolio - Stocks.csv'
    # )
    # cash = OneItemFinancialInstrument('Cash', country='Global')
    # mutual_fund = OneItemFinancialInstrument('Mutual Fund', country='Global')
    # bonds = OneItemFinancialInstrument('Bonds', country='Global')
    # bitcoin = OneItemFinancialInstrument('Bitcoin', country='Global')
    # gold = OneItemFinancialInstrument('Gold', country='Global')
    #
    # portfolio = MultipleItemsFinancialInstrument.aggregate(
    #     [
    #         (0.1947, etf_portfolio),
    #         (0.4259, cash),
    #         (0.1864, stocks_portfolio),
    #         (0., bonds),
    #         (0.1882, mutual_fund),
    #         (0.0049, bitcoin),
    #         (0., gold),
    #     ]
    # )
    # portfolio.export_to_csv()
    # portfolio.statistics_country()
    # portfolio.statistics_sector()
