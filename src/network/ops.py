from typing import Optional

from src import network
from src.factories import get_factory, create_portfolio_google_sheets
from src.instruments import ETF, MultipleItemsFinancialInstrument
from src.settings import SPREAD_SHEET_ID
from src.network.managers import DownloadManager, GoogleSheetsManager


def get_from_network(source: str):
    return {
        'vanguard': None,
        'ishares': get_etf_ishares,
        'sprd': get_etf_spdr,
        'sheets': get_google_sheets,
        'hsbc': None
    }.get(source)


def get_etf_vanguard(ticker: str) -> Optional[ETF]:
    raise NotImplementedError()


def get_etf_ishares(ticker: str) -> Optional[ETF]:
    return _get_etf(ticker, 'ishares')


def get_etf_spdr(ticker: str) -> Optional[ETF]:
    return _get_etf(ticker, 'spdr')


def _get_etf(ticker: str, source: str) -> Optional[ETF]:
    factory = get_factory(source)

    ticker = ticker.upper()
    urls = network.get_urls()

    etf_url = urls['funds'][source].get(ticker, None)
    if etf_url is None:
        return None

    etf_file_name = f'{ticker}.csv'
    with DownloadManager(etf_url, etf_file_name) as d:
        etf_file_path = d.download()
        etf = factory(ticker, etf_file_path)

        return etf


def get_google_sheets(sheet_range: str) -> Optional[MultipleItemsFinancialInstrument]:
    """
        spreadsheet_id: It is found in the sharable google sheet link.
        sheet_range: This could be only the name of the Sheet ( ex: Stocks), files range ( A1:I15),
                or both ( Stocks!A1:I15)

        The first line should contain ONLY the columns of the table.
        Mandatory columns: 'Name', 'Ticker', 'Percentage', 'Type'
    """
    google_sheets_manager = GoogleSheetsManager(SPREAD_SHEET_ID)
    data = google_sheets_manager.read(sheet_range=sheet_range)

    is_only_data_range = '!' not in sheet_range and ':' in sheet_range
    if is_only_data_range:
        financial_instrument_name = f'FinancialInstrumentGoogleSheets!{sheet_range}'
    else:
        financial_instrument_name = sheet_range.split(':')[0]

    financial_instrument = create_portfolio_google_sheets(financial_instrument_name, data)

    return financial_instrument
