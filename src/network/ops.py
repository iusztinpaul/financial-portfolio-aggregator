import json
import os
from pathlib import Path
from typing import Optional

from src.factories import get_factory, create_stocks_portfolio_google_sheets
from src.models import ETF, MultipleItemsFinancialInstrument
from src.settings import STORAGE_PATH, SPREAD_SHEET_ID
from src.network.managers import DownloadManager, GoogleSheetsManager

CURRENT_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))))
URLS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'urls.json'))


def get_etf_vanguard(name: str) -> Optional[ETF]:
    return None


def get_etf_ishares(name: str) -> Optional[ETF]:
    return _get_etf(name, 'ishares')


def get_etf_spdr(name: str) -> Optional[ETF]:
    return _get_etf(name, 'spdr')


def _get_etf(name: str, source: str) -> Optional[ETF]:
    factory = get_factory(source)

    name = name.upper()

    with open(URLS_FILE, 'r') as f:
        urls = json.load(f)

    etf_url = urls['funds'][source].get(name, None)
    if etf_url is None:
        return None

    etf_file_path = f'{STORAGE_PATH}/{name}.csv'
    with DownloadManager(etf_url, etf_file_path) as d:
        d.download()
        etf = factory(name, etf_file_path)

        return etf


def get_stocks_google_sheets(sheet_range: str) -> Optional[MultipleItemsFinancialInstrument]:
    """
        spreadsheet_id: It is found in the sharable google sheet link.
        sheet_range: This could be only the name of the Sheet ( ex: Stocks), data range ( A1:I15),
                or both ( Stocks!A1:I15)

        The first line should contain ONLY the columns of the table.
        Mandatory columns: 'Ticker', 'Name', 'Percentage'
    """
    google_sheets_manager = GoogleSheetsManager(SPREAD_SHEET_ID)
    data = google_sheets_manager.read(sheet_range=sheet_range)

    is_only_data_range = '!' not in sheet_range and ':' in sheet_range
    if is_only_data_range:
        financial_instrument_name = f'FinancialInstrumentGoogleSheets!{sheet_range}'
    else:
        financial_instrument_name = sheet_range.split(':')[0]

    financial_instrument = create_stocks_portfolio_google_sheets(financial_instrument_name, data)

    return financial_instrument
