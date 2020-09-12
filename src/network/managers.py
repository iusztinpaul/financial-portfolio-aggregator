import os
import pickle
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from requests.api import get

from src.exceptions import DownloadError
from src.settings import STORAGE_PATH, GOOGLE_SHEETS_CREDENTIALS_PATH


class DownloadManager:
    def __init__(self, url: str, file_name: str):
        self.url = url
        self.file_name = file_name
        self.file_path = os.path.abspath(os.path.join(STORAGE_PATH, file_name))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Path(self.file_name).exists():
            os.remove(self.file_name)

    def download(self):
        with open(self.file_path, "wb") as file:
            response = get(self.url)

            if response.status_code == 500:
                raise DownloadError(self.file_name)

            file.write(response.content)

        return self.file_path


class GoogleAPIManager:
    SCOPES = []
    API_SERVICE_NAME = None
    API_VERSION = None

    def __init__(self):
        assert len(self.SCOPES) > 0
        assert self.API_SERVICE_NAME is not None
        assert self.API_VERSION is not None

        self.token_name = f'token_{self.API_SERVICE_NAME}_{self.API_VERSION}.pickle'
        self.token_path = os.path.abspath(os.path.join(STORAGE_PATH, self.token_name))
        self.credentials = self._get_credentials()

        self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self.credentials)

    def _get_credentials(self):
        credentials = None

        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
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

            with open(self.token_path, 'wb') as token:
                pickle.dump(credentials, token)

        return credentials

    def read(self, **kwargs):
        raise NotImplementedError()

    def write(self, **kwargs):
        raise NotImplementedError()


class GoogleSheetsManager(GoogleAPIManager):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    API_SERVICE_NAME = 'sheets'
    API_VERSION = 'v4'

    def __init__(self, spreadsheet_id: str):
        super().__init__()
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheets = self.service.spreadsheets()

    def read(self, **kwargs) -> list:
        """
            sheet_range: This could be only the name of the Sheet ( ex: Stocks), files range ( A1:I15),
                or both ( Stocks!A1:I15)
        """

        sheet_range = kwargs.get('sheet_range')
        assert isinstance(sheet_range, str)

        result_input = self.spreadsheets.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range
        ).execute()

        return result_input.get('values', [])

    def write(self, **kwargs):
        data = kwargs.get('data')
        workspace_name = kwargs.get('workspace_name')

        try:
            self.add_workspace(workspace_name)
        except HttpError:
            self.clear_workspace(workspace_name)

        assert isinstance(data, list) and isinstance(data[0], list)
        assert isinstance(workspace_name, str)

        self.spreadsheets.values().update(
            spreadsheetId=self.spreadsheet_id,
            valueInputOption='RAW',
            range=workspace_name,
            body={
                'majorDimension': 'ROWS',
                'values': data
            }
        ).execute()

    def add_workspace(self, name: str):
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': name,
                    }
                }
            }]
        }

        response = self.spreadsheets.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=request_body
        ).execute()

        return response

    def clear_workspace(self, name: str):
        self.spreadsheets.values().clear(
            spreadsheetId=self.spreadsheet_id,
            range=name
        ).execute()
