from abc import abstractmethod
from datetime import timedelta

import numpy as np
import pandas as pd

from src import constants
from src.data_generator.day_ahead_extractors.base_day_ahead_extractor import BaseDayAheadExtractor
from src.data_generator.day_ahead_extractors.utils.mappings import ACTUAL_MAPPING, FORECAST_MAPPING


class PseDataDayAheadExtractor(BaseDayAheadExtractor):
    def extract(self) -> pd.DataFrame:
        data = self.raw_df.copy()
        data = data.replace('-', np.NaN)
        for column in data.columns:
            data[column] = data[column].apply(self.delete_unnecessary_commas_and_add_dot)
        if 'Godzina' in data.columns:
            data_with_timestamps = self._handle_time_shift(data)
            data_with_timestamps = self._get_datetime_from_dates_and_hours(data_with_timestamps)
        else:
            repeated_data = pd.DataFrame(pd.to_datetime(data['Data']).repeat(24))
            repeated_data = repeated_data.sort_values(by='Data').reset_index(drop=True)
            for index, row in repeated_data.iterrows():
                row['Data'] = row['Data'] + timedelta(hours=index % 24)

            repeated_data = repeated_data.rename(columns={'Data': 'date'})
            repeated_data['Data'] = repeated_data['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            data_with_timestamps = pd.merge(repeated_data, data, on='Data')
            data_with_timestamps = data_with_timestamps.drop(columns=['Data'])

        data_indexed = data_with_timestamps.set_index('date')
        mapping = FORECAST_MAPPING if self._get_prediction_flag() else ACTUAL_MAPPING
        data_transformed = data_indexed.rename(columns=mapping)
        return data_transformed

    @staticmethod
    def delete_unnecessary_commas_and_add_dot(x):
        try:
            commas_quantity = x.count(',')
            if commas_quantity > 1:
                for _ in range(commas_quantity - 1):
                    comma_position = x.find(',')
                    x = x[:comma_position] + x[comma_position + 1:]
            x = x.replace(',', '.')
        except AttributeError:
            pass
        return x

    def _get_date_column(self) -> str:
        return 'Data'

    def _get_datetime_from_dates_and_hours(self, data: pd.DataFrame) -> pd.DataFrame:
        date_column = self._get_date_column()
        data[date_column] = pd.to_datetime(data[date_column].astype(str))
        data['date'] = data.apply(
            lambda row: row[date_column] + timedelta(hours=int(row['Godzina']) - 1),
            axis=1,
        )
        data = data.drop(columns=[date_column, 'Godzina'])
        return data

    @abstractmethod
    def _get_prediction_flag(self) -> bool:
        raise NotImplementedError(constants.METHOD_NOT_IMPLEMENTED)

    def _handle_time_shift(self, data: pd.DataFrame) -> pd.DataFrame:
        if any(data['Godzina'] == '2A'):
            data = data[data['Godzina'] != '2A']
            data['Godzina'] = data['Godzina'].astype('int')

        unique_dates = data[self._get_date_column()].unique()
        for date in unique_dates:
            existing_hours = data.loc[data[self._get_date_column()] == date, 'Godzina'].unique()
            if len(existing_hours) == 23:
                # 2 is always missing
                if self.__class__.__name__ == 'RealUnitsOutagesDayAheadExtractor':
                    adjacent_data = data.loc[
                        (data[self._get_date_column()] == date) & (data['Godzina'] == 1)
                        ]
                    adjacent_data['Godzina'] = 2
                else:
                    adjacent_data = data.loc[
                        (data[self._get_date_column()] == date) & (data['Godzina'].isin([1, 3]))
                        ]
                    for column in adjacent_data.columns:
                        adjacent_data[column] = \
                            adjacent_data[column].apply(pd.to_numeric, errors='ignore')
                    adjacent_data = adjacent_data.groupby(by=[self._get_date_column()]).mean()
                    adjacent_data = adjacent_data.reset_index()
                data = pd.concat([data, adjacent_data])
                data = data.sort_values(by=[self._get_date_column(), 'Godzina'])

        return data
