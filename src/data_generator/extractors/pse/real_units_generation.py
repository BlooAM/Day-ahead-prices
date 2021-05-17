from src.data_generator.extractors.pse.base_extractor import BasePseDataExtractor

__all__ = ('RealUnitsGenerationExtractor',)


class RealUnitsGenerationExtractor(BasePseDataExtractor):
    def _get_data_name(self) -> str:
        return 'PL_GEN_MOC_JW_EPS'
