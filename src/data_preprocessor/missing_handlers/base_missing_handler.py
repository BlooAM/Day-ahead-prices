from abc import ABC, abstractmethod

import pandas as pd

from src.constants import METHOD_NOT_IMPLEMENTED


class BaseMissingHandler(ABC):
    @abstractmethod
    def handle(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(METHOD_NOT_IMPLEMENTED)
