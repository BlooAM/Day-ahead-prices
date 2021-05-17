from src.data_generator.day_ahead_extractors.pse.base_day_ahead_extractor import PseDataDayAheadExtractor

__all__ = ('RealBasicDataDayAheadExtractor',)


class RealBasicDataDayAheadExtractor(PseDataDayAheadExtractor):
    def _get_prediction_flag(self) -> bool:
        return False
