import pickle
from datetime import timedelta, datetime
from os import path
from pathlib import Path

from src.data_generator.utils.core import daterange


def load_pse_data(start_day=None, end_day=datetime.now()):
    if start_day is None:
        start_day = end_day - timedelta(days=1)
    pse_data_dict = dict()
    for date in daterange(start_day, end_day):
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        pickle_name = 'pse_data_{}{}{}.pickle'.format(year, month, day)
        base_dir = Path(__file__).parent.parent.parent.parent
        full_path = path.join(base_dir, 'resources', 'pse_data', pickle_name)
        pse_data = None
        if path.isfile(full_path):
            with open(full_path, 'rb') as handle:
                pse_data = pickle.load(handle)
        if pse_data is not None:
            pse_data_dict[pickle_name] = pse_data
    return pse_data_dict
