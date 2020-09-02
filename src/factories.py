from src.models import Holding, ETF
from src.file_normalizers import normalize_ishares_csv_file, normalize_spdr_excel_file, normalize_vanguard_csv_file
import pandas as pd


def create_etf_from_vanguard(etf_name: str, path_to_file: str) -> ETF:
    path_to_file = normalize_vanguard_csv_file(path_to_file)

    etf = ETF(etf_name)
    data_frame = pd.read_csv(path_to_file)
    for index, pandas_holding in data_frame.iterrows():
        try:
            weight = pandas_holding['% of funds']
            if '=' in weight:
                weight = float(weight[2:-2])
            else:
                weight = float(weight[0:-1])
            valid_holding = weight > 0.
        except TypeError:
            valid_holding = False

        if valid_holding:
            holding = Holding(
                name=pandas_holding['Holding name'],
            )

            etf.add_holding_weight(
                holding, weight / 100
            )

    etf.assert_holdings_summed_value()

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
                ticker=pandas_holding['Issuer Ticker'],
                country=pandas_holding['Location'],
                exchange=pandas_holding['Exchange'],
                sector=pandas_holding['Sector'],
                currency=pandas_holding['Market Currency']
            )

            etf.add_holding_weight(
                holding, float(pandas_holding['Weight (%)']) / 100
            )

    etf.assert_holdings_summed_value()

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
