from collections import Iterable
from typing import Optional, Union


def flatten(items: Iterable):
    flattened_list = []

    def _flatten(items_list):
        for item in items_list:
            if isinstance(item, list):
                _flatten(item)
            else:
                if item:
                    flattened_list.append(item)

    _flatten(items)

    return flattened_list


def get_ticker_source(ticker: str, info: dict) -> Optional[str]:
    sources = []

    def _json_look_up(parent_key: str, parent_value: Union[dict, str], ticker: str):
        if ticker in parent_value:
            sources.append(parent_key)

        if isinstance(parent_value, dict):
            [_json_look_up(k, v, ticker) for k, v in parent_value.items()]

    _json_look_up(parent_key='', parent_value=info, ticker=ticker)

    if len(sources) > 0:
        return sources[0]
    else:
        return None


def has_digits(value: str):
    return any(char.isdigit() for char in value)
