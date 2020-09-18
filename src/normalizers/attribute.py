from typing import Optional

from src.choices import HoldingTypeChoices


class HoldingAttributesNormalizer:

    @classmethod
    def normalize_name(cls, name) -> str:
        assert name is not None

        name = name.split(',')[0].strip('\n ')
        name = name.replace('.', ' ')
        name = name.replace('-', ' ')
        name = name.replace('&', ' ')

        name = name.replace('(', '')
        name = name.replace(')', '')

        name_items = name.upper().split(' ')

        # Some names have more than one space --> strip & remove it.
        name_items = [name.strip(' ') for name in name_items if len(name) > 0]
        name_items = [item.capitalize() for item in name_items]

        return ' '.join(name_items)

    @classmethod
    def normalize_sector(cls, sector: str) -> str:
        """
            Normalize sector by Vanguard standards.
        """
        # TODO: Not 100% sure if the mappings are correct.

        if sector in ['Information Technology']:
            return 'Technology'

        if sector in ['Communication']:
            return 'Telecommunications'

        if sector in ['Consumer Discretionary']:
            return 'Consumer Services'

        if sector in ['Consumer Staples']:
            return 'Consumer Goods'

        if sector in ['Materials']:
            return 'Basic Materials'

        return sector

    @classmethod
    def normalize_country(cls, country: str) -> str:
        """
            Normalize country by Vanguard standards.
        """

        if country in ['US', 'U.S.']:
            country = 'United States'

        return country

    @classmethod
    def normalize_type(cls, holding_type: str) -> Optional[HoldingTypeChoices]:
        if holding_type is None:
            return None

        holding_type = holding_type.upper()
        assert holding_type in [holding_type.value for holding_type in HoldingTypeChoices]

        return HoldingTypeChoices(holding_type)
