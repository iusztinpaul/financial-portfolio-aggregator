from src.factories import create_etf_from_vanguard
from src.network.ops import get_etf_ishares, get_etf_spdr, get_stocks_google_sheets
from src.models import MultipleItemsFinancialInstrument

# TODO: Check why get_holding_weight for only ticker equality is not working.
# TODO: Create a new google sheet, sheet programatically.
# TODO: Download VANGUARD etfs files dinamically.
# TODO: Add NYSEMarket support.
# TODO: Add docs.cn
# TODO: Add args for more generic purposes.
# TODO: Add env support for settings
# TODO: Add financial data support.
# TODO: Make a better sector & industry normalization.
# TODO: Improve your model __eq__ method && name_normalize() function


if __name__ == '__main__':
    stocks = get_stocks_google_sheets('Stocks')
    overview = get_stocks_google_sheets('Portfolio')
    etfs = get_stocks_google_sheets('ETFS')

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

    etf_portfolio_distribution = [
            (etfs.get_holding_weight('CSPX', 'CSPX'), cspx_etf),
            (etfs.get_holding_weight('CNDX', 'CNDX'), cndx_etf),
            (etfs.get_holding_weight('IUIT', 'IUIT'), iuit_etf),
            (etfs.get_holding_weight('WCOS', 'WCOS'), wcos_etf),
            (etfs.get_holding_weight('VHYL', 'VHYL'), vhyl_etf),
            (etfs.get_holding_weight('VFEM', 'VFEM'), vfem_etf)
        ]
    etf_portfolio = MultipleItemsFinancialInstrument.aggregate(etf_portfolio_distribution)

    etf_portfolio.export_to_google_sheets()
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
