from src.data_generator.day_ahead_extractors.pse.base_day_ahead_extractor import PseDataDayAheadExtractor

__all__ = ('CO2PriceDayAheadExtractor',)


class CO2PriceDayAheadExtractor(PseDataDayAheadExtractor):
    def _get_prediction_flag(self) -> bool:
        return False
