import json
import os
from typing import Optional

import src.utils as utils
from src.settings import FILES_DIR
from .ops import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_paths():
    with open(f'{CURRENT_DIR}/paths.json', 'r') as f:
        return json.load(f)


def get_source(ticker: str) -> Optional[str]:
    return utils.get_ticker_source(ticker, get_paths())
