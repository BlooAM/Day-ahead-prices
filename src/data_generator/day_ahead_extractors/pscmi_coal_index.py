import pandas as pd

from src.data_generator.day_ahead_extractors.base_day_ahead_extractor import BaseDayAheadExtractor


class PscmiCoalIndexDayAheadExtractor(BaseDayAheadExtractor):
    def extract(self) -> pd.DataFrame:
        return self.raw_df
