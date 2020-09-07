import os
from collections import Iterable
from pathlib import Path

from requests import get


class DownloadManager:
    def __init__(self, url: str, file_name: str):
        self.url = url
        self.file_name = file_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Path(self.file_name).exists():
            os.remove(self.file_name)

    def download(self):
        with open(self.file_name, "wb") as file:
            response = get(self.url)
            file.write(response.content)


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
