import os
import pickle
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
from requests.api import get

from src.exceptions import DownloadError
from src.settings import STORAGE_PATH, GOOGLE_SHEETS_CREDENTIALS_PATH


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

            if response.status_code == 500:
                raise DownloadError(self.file_name)

            file.write(response.content)


class GoogleAPIManager:
    SCOPES = []
    TOKEN_PATH = os.path.abspath(os.path.join(STORAGE_PATH, 'google_api_token.pickle'))

    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def _get_credentials(self):
        credentials = None

        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_SHEETS_CREDENTIALS_PATH,
                    self.SCOPES
                )
                credentials = flow.run_local_server(port=0)

            with open(self.TOKEN_PATH, 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    def read(self, **kwargs):
        raise NotImplementedError()

    def write(self, **kwargs):
        raise NotImplementedError()


class GoogleSheetsManager(GoogleAPIManager):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id: str):
        super().__init__()
        self.spreadsheet_id = spreadsheet_id

    def read(self, **kwargs) -> list:
        sheet_range = kwargs.get('sheet_range')
        assert isinstance(sheet_range, str)

        sheet = self.service.spreadsheets()
        result_input = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range
        ).execute()

        return result_input.get('values', [])

    def write(self, **kwargs):
        data = kwargs.get('data')
        sheet_name = kwargs.get('sheet_name')

        assert isinstance(data, list) and isinstance(data[0], list)
        assert isinstance(sheet_name, str)

        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            valueInputOption='RAW',
            range=sheet_name,
            body={
                'majorDimension': 'ROWS',
                'values': data
            }
        ).execute()
