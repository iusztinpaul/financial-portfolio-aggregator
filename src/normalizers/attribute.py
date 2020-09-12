from typing import Optional

from src.choices import HoldingTypeChoices
from src.utils import flatten


class HoldingAttributesNormalizer:

    @classmethod
    def normalize_name(cls, name) -> str:
        name = name.split(',')[0]

        name_items = name.upper().strip('\n ').split(' ')
        name_items = [item.strip(' ').split('.') for item in name_items]
        name_items = flatten(name_items)

        name_items = [item.strip('. ').capitalize() for item in name_items]

        return ' '.join(name_items)

    @classmethod
    def normalize_country(cls, country: str) -> str:
        if country in ['United States', 'U.S.']:
            country = 'US'

        return country

    @classmethod
    def normalize_type(cls, holding_type: str) -> Optional[HoldingTypeChoices]:
        if holding_type is None:
            return None

        holding_type = holding_type.upper()
        assert holding_type in [holding_type.value for holding_type in HoldingTypeChoices]

        return HoldingTypeChoices(holding_type)
