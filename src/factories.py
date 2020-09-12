import os
from pathlib import Path
from typing import List

from src.instruments import Holding, ETF, MultipleItemsFinancialInstrument
from src.normalizers.file import normalize_ishares_csv_file, normalize_spdr_excel_file, normalize_vanguard_csv_file
import pandas as pd

from src.normalizers.structures import normalize_google_sheets_list


def get_factory(source: str):
    return {
        'vanguard': create_etf_from_vanguard,
        'ishares': create_etf_from_ishares_csv,
        'spdr': create_etf_from_spdr_excel,
        'custom': create_etf_from_custom_csv,
        'hsbc': None
    }[source]


def create_etf_from_vanguard(etf_name: str, path_to_file: str) -> ETF:
    def extract_from_field(field: str):
        if '=' in field:
            return field[2:-2]
        else:
            return field

    path_to_file = normalize_vanguard_csv_file(path_to_file)

    etf = ETF(etf_name)
    data_frame = pd.read_csv(path_to_file)
    for index, pandas_holding in data_frame.iterrows():
        try:
            weight = float(extract_from_field(pandas_holding['% of funds']))
        except TypeError:
            weight = -1

        if weight > 0:
            holding = Holding(
                name=extract_from_field(pandas_holding['Holding name']),
            )

            etf.add_holding_weight(
                holding, weight / 100
            )

    etf.assert_holdings_summed_value()
    if Path(path_to_file).exists():
        os.remove(path_to_file)

    return etf


def create_etf_from_ishares_csv(etf_name: str, path_to_file: str) -> ETF:
    path_to_file = normalize_ishares_csv_file(path_to_file)

    etf = ETF(etf_name)
    data_frame = pd.read_csv(path_to_file)
    for index, pandas_holding in data_frame.iterrows():
        try:
            valid_holding = float(pandas_holding['Weight (%)']) > 0.
        except ValueError:
            valid_holding = False

        if valid_holding:
            holding = Holding(
                name=pandas_holding['Name'],
                ticker=pandas_holding.get('Issuer Ticker') or pandas_holding.get('Ticker'),
                country=pandas_holding['Location'],
                exchange=pandas_holding['Exchange'],
                sector=pandas_holding['Sector'],
                currency=pandas_holding['Market Currency']
            )

            etf.add_holding_weight(
                holding, float(pandas_holding['Weight (%)']) / 100
            )

    etf.assert_holdings_summed_value()
    if Path(path_to_file).exists():
        os.remove(path_to_file)

    return etf


def create_etf_from_spdr_excel(etf_name: str, path_to_file: str) -> ETF:
    path_to_file = normalize_spdr_excel_file(path_to_file)

    etf = ETF(etf_name)
    data_frame = pd.read_csv(path_to_file)
    for index, pandas_holding in data_frame.iterrows():
        try:
            valid_holding = float(pandas_holding['Percent Of Fund']) > 0.
        except ValueError:
            valid_holding = False

        if valid_holding:
            holding = Holding(
                name=pandas_holding['Security Name'],
                country=pandas_holding['Trade Country Name'],
                sector=pandas_holding['Sector Classification'],
                industry=pandas_holding['Industry Classification'],
                currency=pandas_holding['Currency']
            )

            etf.add_holding_weight(
                holding, float(pandas_holding['Percent Of Fund']) / 100
            )

    etf.assert_holdings_summed_value()
    if Path(path_to_file).exists():
        os.remove(path_to_file)

    return etf


def create_etf_from_custom_csv(etf_name: str, path_to_file: str) -> ETF:
    etf = ETF(etf_name)

    data_frame = pd.read_csv(path_to_file)
    for index, pandas_holding in data_frame.iterrows():
        try:
            valid_holding = float(pandas_holding['Actual Percentage (%)']) > 0.
        except ValueError:
            valid_holding = False

        if valid_holding:
            holding = Holding(
                name=pandas_holding['Company'],
                ticker=pandas_holding['Ticker'],
                country=pandas_holding['Region'],
                sector=pandas_holding['Domain'],
            )

            etf.add_holding_weight(
                holding, float(pandas_holding['Actual Percentage (%)']) / 100
            )

    etf.assert_holdings_summed_value()

    return etf


def create_portfolio_google_sheets(name: str, data: List[list]) -> MultipleItemsFinancialInstrument:
    data = normalize_google_sheets_list(data)

    financial_instrument = MultipleItemsFinancialInstrument(name)
    data_frame = pd.DataFrame(data[1:], columns=data[0])
    for _, pandas_holding in data_frame.iterrows():
        try:
            weight = float(pandas_holding['Percentage']) / 100
        except ValueError:
            try:
                weight = float(pandas_holding['Percentage'][:-1]) / 100
            except ValueError:
                weight = 0

        is_valid = weight > 0

        if is_valid:
            holding = Holding(
                name=pandas_holding['Name'],
                ticker=pandas_holding['Ticker'],
                holding_type=pandas_holding['Type']
            )

            financial_instrument.add_holding_weight(holding, weight)

    return financial_instrument
