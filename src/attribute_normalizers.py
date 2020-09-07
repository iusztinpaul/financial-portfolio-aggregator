from src.utils import flatten


def normalize_name(name):
    name = name.split(',')[0]

    name_items = name.upper().strip('\n ').split(' ')
    name_items = [item.strip(' ').split('.') for item in name_items]
    name_items = flatten(name_items)

    name_items = [item.strip('. ').capitalize() for item in name_items]

    return ' '.join(name_items)


def normalize_country(country: str):
    if country in ['United States', 'U.S.']:
        country = 'US'

    return country
