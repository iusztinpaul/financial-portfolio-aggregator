import json
import os
from pathlib import Path
from typing import Optional

from src.factories import create_etf_from_ishares_csv, create_etf_from_spdr_excel, get_factory
from src.models import ETF
from src.settings import STORAGE_PATH
from src.utils import DownloadManager

CURRENT_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))))
URLS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'urls.json'))


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
