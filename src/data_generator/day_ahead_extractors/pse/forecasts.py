from src.data_generator.day_ahead_extractors.pse.base_day_ahead_extractor import PseDataDayAheadExtractor

__all__ = ('ForecastsDayAheadExtractor',)


# doesn't work after 01.01.2021
class ForecastsDayAheadExtractor(PseDataDayAheadExtractor):
    def _get_prediction_flag(self) -> bool:
        return True
