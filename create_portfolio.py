from src.network.ops import get_google_sheets

# TODO: Change Yahoo source for better region & sector information.
# TODO: Download VANGUARD, HSBC etfs files dinamically.
# TODO: Add more financial data to the markets & aggregate data with them.


if __name__ == '__main__':
    portfolio = get_google_sheets('Portfolio')
    portfolio = portfolio.to_leaves()

    portfolio.export_to_google_sheets(workspace_name='Aggregated')
    portfolio.statistics_country()
    portfolio.statistics_sector()
