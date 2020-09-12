from src.network.ops import get_google_sheets

# TODO: Add a more appropiate OneInstrument sector, country & ticker logic.
# TODO: Download VANGUARD etfs files dinamically.
# TODO: See why, for example, ALIBABA has US as region ( NYSE).
# TODO: Add docs.cn
# TODO: Add args for more generic purposes.
# TODO: Add env support for settings
# TODO: Add financial files support.
# TODO: Make a better sector & industry normalization.
# TODO: Improve your model __eq__ method && name_normalize() function


if __name__ == '__main__':
    portfolio = get_google_sheets('Portfolio')
    portfolio = portfolio.to_leaves()

    portfolio.export_to_google_sheets()
    portfolio.statistics_country()
    portfolio.statistics_sector()
