import os

import pandas as pd

from collections import Counter

from src.utils import has_digits

"""
    A normalized file has to check the following criterias:
        - be a csv file
        - can be read by pandas read_csv(path_to_file)
        - the number of items in a row has to be the same as the number of columns
"""


def normalize_vanguard_csv_file(path_to_file: str) -> str:
    # return normalize_file_by_cutting_lines(path_to_file, 2)
    return normalize_csv_file(path_to_file)


def normalize_ishares_csv_file(path_to_file: str) -> str:
    # return normalize_file_by_cutting_lines(path_to_file, 2)
    return normalize_csv_file(path_to_file)


def normalize_spdr_excel_file(path_to_file: str) -> str:
    data_frame = pd.read_excel(path_to_file)

    path_without_extension = path_to_file.split('.xlsx')[0]
    new_path_to_file = f'{path_without_extension}.csv'
    data_frame.to_csv(new_path_to_file, encoding='utf-8', index=False)

    # return normalize_file_by_cutting_lines(new_path_to_file, 5)
    return normalize_csv_file(path_to_file)


def normalize_file_by_cutting_lines(path_to_file: str, lines_to_cut: int) -> str:
    with open(path_to_file, 'r') as f:
        lines = f.readlines()
        normalized_lines = lines[lines_to_cut:]

    # TODO: Delete this line after downloading VANGUARD dinamically from site.
    if '(' in path_to_file and ')' in path_to_file:
        path_to_file = f'{path_to_file.split(".csv")[0]}_normalized.csv'

    with open(path_to_file, 'w') as f:
        f.writelines(normalized_lines)

    return path_to_file


# TODO: Try to improve this generic normalization function.
def normalize_csv_file(path_to_file: str) -> str:
    def valid_line_rule(line, num_items):
        if num_items <= 3:
            return False

        if has_digits(line) and num_items <= 5:
            return False

        return True

    with open(path_to_file, 'r') as f:
        lines = f.readlines()

        items_per_line = [len(line.split(',')) for line in lines]

        normalized_lines = [
            line for line, num_items in zip(lines, items_per_line)
            if valid_line_rule(line, num_items)
        ]

    # TODO: Delete this line after downloading VANGUARD dinamically from site.
    if '(' in path_to_file and ')' in path_to_file:
        path_to_file = f'{path_to_file.split(".csv")[0]}_normalized.csv'

    with open(path_to_file, 'w') as f:
        f.writelines(normalized_lines)

    return path_to_file
