from src.network.ops import get_google_sheets

# TODO: Refactor CustomDataMarket.
# TODO: Add docs.cn
# TODO: Add args for more generic purposes.
# TODO: Add env support for settings
# TODO: Make a better sector & industry normalization: BUGS
# TODO: Improve your model __eq__ method && name_normalize() function

# TODO: Change Yahoo source for better region & sector information.
# TODO: Download VANGUARD etfs files dinamically.
# TODO: Add financial files support.


if __name__ == '__main__':
    portfolio = get_google_sheets('Portfolio')
    portfolio = portfolio.to_leaves()

    portfolio.export_to_google_sheets(workspace_name='Aggregated')
    portfolio.statistics_country()
    portfolio.statistics_sector()
