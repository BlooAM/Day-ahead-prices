from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, date: datetime) -> pd.DataFrame:
        raise NotImplementedError('Method not implemented')
