from pathlib import Path

STORAGE_PATH = str(Path.home() / '.financial-portfolio-aggregator')
Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)

GOOGLE_SHEETS_CREDENTIALS_PATH = \
    '/home/peius/Documents/Projects/financial-portfolio-aggregator/credentials/credentials.json'
SPREAD_SHEET_ID = '1a7InF7c2iPDBLs90fm62DqxjhMLVWBGKralqrq4TTag'
