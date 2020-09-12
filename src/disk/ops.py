import os
from typing import Optional

from src.factories import create_etf_from_vanguard
from src.instruments import ETF
from src.settings import FILES_DIR


def get_from_disk(source: str):
    return {
        'vanguard': get_etf_vanguard,
        'ishares': None,
        'sprd': None,
        'sheets': None,
        'hsbc': None
    }.get(source)


def get_etf_vanguard(ticker: str) -> Optional[ETF]:
    from src.disk import get_paths

    ticker = ticker.upper()
    file_path = get_paths()['funds']['vanguard'][ticker]
    file_path = os.path.abspath(os.path.join(FILES_DIR, file_path))

    return create_etf_from_vanguard(ticker, file_path)

