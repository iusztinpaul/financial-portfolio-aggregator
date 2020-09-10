import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_urls():
    with open(f'{CURRENT_DIR}/urls.json', 'r') as f:
        return json.load(f)
