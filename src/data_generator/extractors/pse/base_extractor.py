import io
import os
import pickle
from abc import abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from src.utils.core import get_resources_path
from src.data_generator.extractors.base_extractor import BaseExtractor


class PseRequestFailureException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class BasePseDataExtractor(BaseExtractor):
    def __init__(self):
        self.extractor_name = self.__class__.__name__

    def extract(self, date: datetime) -> pd.DataFrame:
        date_formatted = date.strftime('%Y%m%d')

        data = self.__read_data_from_local_directory(date=date_formatted)
        if data is None:
            data = self.__download_data_from_pse_website(date=date_formatted)

        return data

    @abstractmethod
    def _get_data_name(self) -> str:
        raise NotImplementedError('Method not implemented')

    def __read_data_from_local_directory(self, date: str) -> Optional[pd.DataFrame]:
        resource_path = get_resources_path()
        pickle_name = f'pse_data_{date}.pickle'
        pickle_path = os.path.join(resource_path, pickle_name)
        if os.path.isfile(pickle_path):
            with open(pickle_path, 'rb') as handle:
                pse_data = pickle.load(handle)
            df = pse_data.get(self.extractor_name)
            if df is not None:
                return df

    def __download_data_from_pse_website(self, date: str) -> pd.DataFrame:
        data_name = self._get_data_name()
        url = f'https://www.pse.pl/getcsv/-/export/csv/{data_name}/data/{date}'
        r = requests.get(url)
        if r.ok:
            data = r.content.decode('cp1250')
            return pd.read_csv(io.StringIO(data), sep=';')
        else:
            raise PseRequestFailureException(f'Request failed. Data: {data_name}. Date: {date}')
