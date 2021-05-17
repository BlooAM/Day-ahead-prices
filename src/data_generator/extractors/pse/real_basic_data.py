from src.data_generator.extractors.pse.base_extractor import BasePseDataExtractor

__all__ = ('RealBasicDataExtractor',)


class RealBasicDataExtractor(BasePseDataExtractor):
    def _get_data_name(self) -> str:
        return 'PL_WYK_KSE'
