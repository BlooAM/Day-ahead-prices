from datetime import datetime

import pandas as pd
import holidays
from src.data_generator.day_ahead_extractors.utils.day_ahead_extractors_loader import \
    load_day_ahead_extractors


class BasicPipeline:
    def __init__(self, start_day=datetime.now(), end_day=None):
        self.start_day = start_day
        self.end_day = end_day

    def fit(self):
        start = pd.Timestamp(self.start_day).normalize()
        end = pd.Timestamp(self.end_day).normalize()
        self.df = pd.DataFrame(
            index=pd.date_range(start=start, end=end, freq='1H', normalize=True, closed='left')
        )
        self.df['holiday'] = self.df.index.to_series().map(lambda x: int(x in holidays.PL() or x.weekday() in [5, 6]))
        self.df['peak7'] = self.df.index.to_series().map(lambda x: int(x.hour in range(7, 22)))
        self.df['peak5'] = ((self.df['holiday'] == 0) & (self.df['peak7'] == 1)).map(int)
        prediction_day = self.df.index + pd.Timedelta('1 days')
        weekday = prediction_day.weekday
        month = prediction_day.month
        self.df = self.df.assign(weekday=weekday, month=month)
        return self

    def transform(self):
        day_ahead_extractors = load_day_ahead_extractors()
        day_ahead_extractors_data_batches = list()
        for day_ahead_extractor_name, DayAheadExtractor in day_ahead_extractors.items():
            if day_ahead_extractor_name not in ['RealUnitsOutagesTransformer']:
                day_ahead_extractors_data_batches.append(
                    DayAheadExtractor(self.start_day, self.end_day).extract()
                )

        return self.df.join(day_ahead_extractors_data_batches)

    def fit_transform(self):
        return self.fit().transform()


if __name__ == '__main__':
    start_day = datetime(2020, 12, 1)
    end_day = datetime(2020, 12, 31)
    pipeline = BasicPipeline(start_day, end_day)
    df = pipeline.fit_transform()
