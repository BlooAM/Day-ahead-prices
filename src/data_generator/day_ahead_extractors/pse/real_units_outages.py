from datetime import datetime

import pandas as pd

from src.data_generator.day_ahead_extractors.pse.base_day_ahead_extractor import PseDataDayAheadExtractor

__all__ = ('RealUnitsOutagesDayAheadExtractor',)


class RealUnitsOutagesDayAheadExtractor(PseDataDayAheadExtractor):
    def extract(self) -> pd.DataFrame:
        raw_data_copy = self.raw_df.copy()

        for column in ['Wielkość ubytku elektrownianego', 'Wielkość ubytku sieciowego',
                       'Dostępne zdolności wytwórcze']:
            raw_data_copy[column] = \
                raw_data_copy[column].apply(self.delete_unnecessary_commas_and_add_dot)
            raw_data_copy[column] = raw_data_copy[column].astype('float')

        data_with_complete_columns = self._handle_time_shift(data=raw_data_copy)
        data_transformed = self._get_datetime_from_dates_and_hours(data_with_complete_columns)
        data_transformed = data_transformed.rename(
            columns={'Kod JW': 'code', 'Wielkość ubytku elektrownianego': 'outage'}
        )
        data_transformed = data_transformed[['date', 'code', 'outage']]

        unit_static_data = pd.read_csv('resources/unit_codes_by_sources.csv')
        installed_capacity = unit_static_data[['unit_code_pse', 'capacity_installed', 'unit_type']]
        data_with_capacity_installed = \
            pd.merge(data_transformed, unit_static_data, left_on='code', right_on='unit_code_pse')

        data_with_capacity_classes = \
            self.__divide_into_unit_classes(data=data_with_capacity_installed)
        data_by_capacity_and_type = \
            data_with_capacity_classes.groupby(by=['date', 'unit_type', 'capacity_class']).sum()
        data_by_capacity_and_type = data_by_capacity_and_type.reset_index()
        data_by_capacity_and_type = \
            data_by_capacity_and_type[['date', 'unit_type', 'capacity_class', 'outage']]

        installed_capacity_with_capacity_classes = \
            self.__divide_into_unit_classes(data=installed_capacity)
        installed_capacity_by_capacity_and_type = installed_capacity_with_capacity_classes.groupby(
            by=['unit_type', 'capacity_class']
        ).sum().reset_index()

        data_transformed = pd.merge(data_by_capacity_and_type,
                                    installed_capacity_by_capacity_and_type,
                                    on=['unit_type', 'capacity_class'],
                                    )
        data_transformed['available_capacity'] = \
            data_transformed['capacity_installed'] - data_transformed['outage']
        available_capacity = data_transformed.pivot(
            index='date',
            columns=['unit_type', 'capacity_class'],
            values='available_capacity',
        )
        total_capacity = installed_capacity_by_capacity_and_type.pivot(
            columns=['unit_type', 'capacity_class'],
            values='capacity_installed',
        ).bfill()

        for column in total_capacity.columns:
            capacity_installed = total_capacity[column][0]
            if column not in available_capacity.columns:
                available_capacity[column] = capacity_installed
            available_capacity[column].fillna(capacity_installed, inplace=True)

        columns = [' '.join(col) + ' available' for col in available_capacity.columns]
        available_capacity.columns = columns
        return available_capacity

    def _get_prediction_flag(self) -> bool:
        return True

    def __divide_into_unit_classes(self, data: pd.DataFrame) -> pd.DataFrame:
        data['capacity_class'] = pd.cut(
            x=data['capacity_installed'],
            bins=[0, 100, 300, 400, 700, 9999],
            labels=['100', '200', '300', '500', '1000'],
        ).astype(str)
        return data


if __name__ == '__main__':
    from src.data_generator.extractors.pse.real_units_outages import RealUnitsOutagesExtractor
    df = RealUnitsOutagesExtractor().extract(date=datetime(2020, 3, 29))

    transformed = RealUnitsOutagesDayAheadExtractor(
        start_date=datetime(2020, 3, 29),
        end_date=datetime(2020, 6, 30),
    ).extract()
