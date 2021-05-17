import os
from importlib import import_module
from inspect import isclass
from os import walk
from os.path import abspath, basename, dirname, join
from sys import modules

from src.data_generator.day_ahead_extractors.base_day_ahead_extractor import BaseDayAheadExtractor

__all__ = ('load_day_ahead_extractors',)

PROJ_DIR = abspath(join(dirname(abspath(__file__)), '../../..'))
PROJ_MODULE = basename(PROJ_DIR)
CURR_DIR = os.path.join(PROJ_DIR, 'data_generator', 'day_ahead_extractors')
CURR_MODULE = basename(CURR_DIR)
DAY_AHEAD_EXTRACTOR_TYPES = [
    'pse',
#    'producers',
]


def get_modules(module):
    module_directory = abspath(join(CURR_DIR, module))
    for root, dir_names, files in walk(module_directory):
        module_path_end = root.split(CURR_MODULE)[1].replace('\\', '.')
        module_path = f'{PROJ_MODULE}.data_generator.{CURR_MODULE}{module_path_end}'
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__init__'):
                yield '.'.join([module_path, filename[0:-3]])


def dynamic_loader(module, compare):
    items = []
    for mod in get_modules(module):
        module = import_module(mod)
        if hasattr(module, '__all__'):
            objs = [getattr(module, obj) for obj in module.__all__]
            items += [o for o in objs if o not in items and compare(o)]
    return items


def is_day_ahead_extractor(item):
    return isclass(item) and issubclass(item, BaseDayAheadExtractor)


def get_day_ahead_extractor(day_ahead_extractor_type):
    return dynamic_loader(day_ahead_extractor_type, is_day_ahead_extractor)


def load_day_ahead_extractors():
    day_ahead_extractors = dict()
    for day_ahead_extractor_type in DAY_AHEAD_EXTRACTOR_TYPES:
        for day_ahead_extractor in get_day_ahead_extractor(day_ahead_extractor_type):
            setattr(modules[__name__], day_ahead_extractor.__name__, day_ahead_extractor)
            day_ahead_extractors[day_ahead_extractor.__name__] = day_ahead_extractor
    return day_ahead_extractors
