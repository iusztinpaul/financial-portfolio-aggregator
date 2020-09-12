from typing import List


def normalize_google_sheets_list(data: List[list]) -> List[list]:
    standard_len = len(data[0])

    new_data = []
    for i, line in enumerate(data):
        if 'Total' in line:
            continue
        if 'TOTAL' in line:
            continue

        line_len = len(line)
        if line_len > standard_len:
            new_data.append(line[:standard_len])
        elif line_len > 0:
            new_data.append(line)

    return new_data
