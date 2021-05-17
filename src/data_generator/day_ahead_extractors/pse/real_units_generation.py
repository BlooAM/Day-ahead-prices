import pandas as pd

from src.data_generator.day_ahead_extractors.pse.base_day_ahead_extractor import PseDataDayAheadExtractor

__all__ = ('RealUnitsGenerationDayAheadExtractor',)


class RealUnitsGenerationDayAheadExtractor(PseDataDayAheadExtractor):
    def extract(self):
        raw_data_copy = self.raw_df.copy()
        raw_data_copy = raw_data_copy[raw_data_copy['Tryb pracy'] == 'Generacja']

        for column in [str(i) for i in range(1, 25)]:
            raw_data_copy[column] = \
                raw_data_copy[column].apply(self.delete_unnecessary_commas_and_add_dot)
            raw_data_copy[column] = raw_data_copy[column].astype('float')

        data_with_complete_columns = self._handle_time_shift(data=raw_data_copy)

        data_transformed = pd.melt(data_with_complete_columns,
                                   id_vars=['Doba', 'Kod'],
                                   value_vars=[str(i) for i in range(1, 25)],
                                   var_name='Godzina',
                                   value_name='power',
                                   )

        data_transformed = self._get_datetime_from_dates_and_hours(data_transformed)
        data_transformed = data_transformed.rename(columns={'Kod': 'code'})
        data_transformed = data_transformed[['date', 'code', 'power']]

        unit_static_data = pd.read_csv('unit_codes_by_sources.csv')
        unit_static_data = unit_static_data[['unit_code_pse', 'capacity_installed', 'unit_type']]
        data_with_capacity_installed = \
            pd.merge(data_transformed, unit_static_data, left_on='code', right_on='unit_code_pse')

        data_with_capacity_classes = self.__divide_into_unit_classes(data_with_capacity_installed)
        data_by_capacity_and_type = \
            data_with_capacity_classes.groupby(by=['date', 'unit_type', 'capacity_class']).sum()
        data_by_capacity_and_type = data_by_capacity_and_type.reset_index()

        data_transformed = data_by_capacity_and_type.pivot(
            index='date',
            columns=['unit_type', 'capacity_class'],
            values='power',
        )
        columns = [' '.join(col) + ' generation' for col in data_transformed.columns]
        data_transformed.columns = columns
        return data_transformed

    def _get_prediction_flag(self) -> bool:
        return False

    def _get_date_column(self) -> str:
        return 'Doba'

    def _handle_time_shift(self, data: pd.DataFrame) -> pd.DataFrame:
        columns = data.columns
        if '2A' in columns:
            data = data.drop(columns=['2A'])
        elif '2' not in columns:
            data['2'] = data[['1', '3']].mean(axis=1)
        elif data['2'].isna().any():
            data.loc[data['2'].isna(), '2'] = data.loc[data['2'].isna(), ['1', '3']].mean(axis=1)
        return data

    def __divide_into_unit_classes(self, data: pd.DataFrame) -> pd.DataFrame:
        data['capacity_class'] = pd.cut(
            x=data['capacity_installed'],
            bins=[0, 100, 300, 400, 700, 9999],
            labels=['100', '200', '300', '500', '1000'],
        ).astype(str)
        return data
