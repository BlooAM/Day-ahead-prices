import pandas as pd

from src.data_preprocessor.missing_handlers.base_missing_handler import BaseMissingHandler


class SolarGenerationMissingHandler(BaseMissingHandler):
    def handle(self, data: pd.DataFrame, solar_generation_column_name: str = 'generation_solar_actual') -> pd.DataFrame:
        missing_solar_data = data[data[solar_generation_column_name].isnull()]
        complete_data = data[~data[solar_generation_column_name].isnull()]
        if not missing_solar_data.empty:
            actual_solar_generation = self._read_actual_solar_generation()
            solar_data = pd.merge(missing_solar_data, actual_solar_generation, left_index=True, right_index=True)
            solar_data[solar_generation_column_name] = solar_data['system_generation'].round(3)
            solar_data.drop(columns=['system_generation'], inplace=True)
            complete_data = pd.concat([complete_data, solar_data])
            complete_data.sort_index(inplace=True)
        return complete_data

    def _read_actual_solar_generation(self):
        solar_generation_profile = pd.read_pickle('resources/pv_profile.pkl')
        solar_generation = solar_generation_profile[['date', 'system_generation']]
        solar_generation.set_index('date', inplace=True)
        return solar_generation


if __name__ == '__main__':
    from src.data_generator.basic_pipeline import BasicPipeline
    from datetime import datetime

    start_day = datetime(2020, 4, 1)
    end_day = datetime(2020, 4, 30)
    pipeline = BasicPipeline(start_day, end_day)
    df = pipeline.fit_transform()

    handled = SolarGenerationMissingHandler().handle(data=df)
