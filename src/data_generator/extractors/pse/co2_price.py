from src.data_generator.extractors.pse.base_extractor import BasePseDataExtractor

__all__ = ('CO2PriceExtractor',)


class CO2PriceExtractor(BasePseDataExtractor):
    def _get_data_name(self) -> str:
        return 'PL_CENY_ROZL_CO2'
