from src.data_generator.extractors.pse.base_extractor import BasePseDataExtractor

__all__ = ('RealExchangesExtractor',)


class RealExchangesExtractor(BasePseDataExtractor):
    def _get_data_name(self) -> str:
        return 'PL_WYK_WYM'
