import os
import pickle
from pathlib import Path

from src.data_generator.extractors.utils.extractors_loader import load_extractors
from src.data_generator.utils.core import daterange


def dump_pse_data(start_day, end_day, echo=False):
    for date in daterange(start_day, end_day):
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        pickle_name = f'pse_data_{year}{month}{day}.pickle'
        base_dir = Path(__file__).parent.parent.parent.parent.parent
        full_path = os.path.join(base_dir, 'resources', 'pse_data', pickle_name)

        pse_extractors = load_extractors()
        pse_data = dict()
        if os.path.isfile(full_path):
            if echo:
                print('File {} already exists'.format(pickle_name))
        else:
            try:
                for extractor_name, extractor in pse_extractors.items():
                        pse_data[extractor_name] = extractor().extract(date=date)
            except Exception as e:
                pse_data = None
                if echo:
                    print(f'Exception has occured with following error message:\n{e}')
            if pse_data is not None:
                with open(full_path, 'wb') as handle:
                    pickle.dump(pse_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    from datetime import datetime
    dump_pse_data(datetime(2017, 9, 4), datetime(2017, 9, 5), echo=True)
