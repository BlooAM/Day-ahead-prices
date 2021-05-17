from datetime import datetime, time

import pandas as pd

from src.data_generator.extractors.base_extractor import BaseExtractor


class PscmiCoalIndexExtractor(BaseExtractor):
    _DATA_PATH = 'resources/PSCMI_1.csv'

    def extract(self, date: datetime) -> pd.DataFrame:
        date_truncated_to_month = datetime.combine(date, time()).replace(day=1)
        pscmi = pd.read_csv(self._DATA_PATH, parse_dates=['date'])
        pscmi_truncated_to_month = pscmi[pscmi['date'] == date_truncated_to_month]
        if pscmi_truncated_to_month.empty:
            pscmi_truncated_to_month = pscmi[pscmi['date'] == pscmi['date'].max()]
        pscmi_truncated_to_month['date'] = date
        pscmi_truncated_to_month.reset_index(drop=True, inplace=True)
        return pscmi_truncated_to_month
