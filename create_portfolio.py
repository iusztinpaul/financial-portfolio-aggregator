from src.network.ops import get_etf_ishares, get_stocks_google_sheets
from src.instruments import MultipleItemsFinancialInstrument, OneItemFinancialInstrument

# TODO: Add a more appropiate OneInstrument sector, country & ticker logic.
# TODO: Download VANGUARD etfs files dinamically.
# TODO: See why, for example, ALIBABA has US as region ( NYSE).
# TODO: Create a coupling method that starts from the overview & dinamically computes the tree.
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

    etf_portfolio_distribution = [
            (etfs.get_holding_weight('S&P 500'), cspx_etf),
            (etfs.get_holding_weight('NASDAQ 100'), cndx_etf),
            (etfs.get_holding_weight('s&p 500 information technology'), iuit_etf),
        ]
    etf_portfolio = MultipleItemsFinancialInstrument.aggregate(etf_portfolio_distribution)

    portfolio = MultipleItemsFinancialInstrument.aggregate(
        [
            (overview.get_holding_weight('ETFS'), etf_portfolio),
            (overview.get_holding_weight('Cash'), OneItemFinancialInstrument('Cash')),
            (overview.get_holding_weight('Stocks'), stocks),
            (overview.get_holding_weight('Mutual Funds'), OneItemFinancialInstrument('Mutual Funds')),
            (overview.get_holding_weight('Bitcoin'), OneItemFinancialInstrument('Bitcoin')),
        ]
    )
    portfolio.export_to_google_sheets()
    portfolio.statistics_country()
    portfolio.statistics_sector()
