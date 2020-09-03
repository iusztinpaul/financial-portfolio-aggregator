from collections import Iterable


def normalize_name(name):
    name_items = name.upper().strip('\n ').split(' ')
    name_items = [item.strip(' ').split('.') for item in name_items]
    name_items = flatten(name_items)

    name_items = [item.strip('. ').capitalize() for item in name_items]

    return ' '.join(name_items)


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


def normalize_country(country: str):
    if country == 'United States':
        country = 'U.S.'

    return country
