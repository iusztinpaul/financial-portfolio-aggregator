import datetime
import os
from pathlib import Path

import typing
from dotenv import load_dotenv
from marshmallow import Schema, fields, validates_schema, types

PROJECT_DIR = Path().absolute()
ENV_PATH = PROJECT_DIR / '.env'

load_dotenv(ENV_PATH)


class EnvVarsValidator(Schema):
    FILES_DIR = fields.String(missing=str(PROJECT_DIR / 'files'))
    STORAGE_PATH = fields.String(missing=str(Path.home() / '.financial-portfolio-aggregator'))

    GOOGLE_SHEETS_CREDENTIALS_PATH = fields.String(missing='./credentials.json')
    SPREAD_SHEET_ID = fields.String(missing=None)

    MARKET_CACHE_EXPIRATION_DAYS = fields.Integer(missing=31)

    @validates_schema
    def validate(
        self,
        data: typing.Mapping,
        *,
        many: bool = None,
        partial: typing.Union[bool, types.StrSequenceOrSet] = None
    ) -> typing.Dict[str, typing.List[str]]:
        pass


ENV_VARS = EnvVarsValidator().load(data=os.environ, many=None, partial=None, unknown='EXCLUDE')

FILES_DIR = ENV_VARS['FILES_DIR']
STORAGE_PATH = ENV_VARS['STORAGE_PATH']
Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)

GOOGLE_SHEETS_CREDENTIALS_PATH = ENV_VARS['GOOGLE_SHEETS_CREDENTIALS_PATH']
SPREAD_SHEET_ID = ENV_VARS['SPREAD_SHEET_ID']

MARKET_CACHE_EXPIRATION_DAYS = ENV_VARS['MARKET_CACHE_EXPIRATION_DAYS']
MARKET_CACHE_EXPIRATION_DAYS = datetime.timedelta(days=MARKET_CACHE_EXPIRATION_DAYS)
