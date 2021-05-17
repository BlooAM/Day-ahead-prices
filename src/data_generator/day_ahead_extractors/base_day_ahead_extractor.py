from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd

from src.data_generator.extractors.utils.extractors_loader import load_extractors
from src.data_generator.utils.core import daterange


class BaseDayAheadExtractor(ABC):
    def __init__(self, start_date: datetime, end_date: datetime):
        self.prediction_flag = False
        extractor_name = self.__class__.__name__.replace('DayAheadExtractor', 'Extractor')
        extractors = load_extractors()
        Extractor = extractors.get(extractor_name)
        self.extractor = Extractor()
        extractor_data_container = list()
        for date in daterange(start_date, end_date):
            extractor_data_container.append(self.extractor.extract(date))

        self.raw_df = pd.concat(extractor_data_container)

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        raise NotImplementedError('Method not implemented')
