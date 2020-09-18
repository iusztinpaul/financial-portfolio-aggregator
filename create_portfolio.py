from src.network.ops import get_google_sheets

# TODO: Add docs.cn
# TODO: Add default env var.
# TODO: Check where credentials.json are automatically generated.

# TODO: Change Yahoo source for better region & sector information.
# TODO: Download VANGUARD etfs files dinamically.
# TODO: Add financial files support.


if __name__ == '__main__':
    portfolio = get_google_sheets('Portfolio')
    portfolio = portfolio.to_leaves()

    portfolio.export_to_google_sheets(workspace_name='Aggregated')
    portfolio.statistics_country()
    portfolio.statistics_sector()
