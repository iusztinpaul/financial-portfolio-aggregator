from collections import Iterable


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
