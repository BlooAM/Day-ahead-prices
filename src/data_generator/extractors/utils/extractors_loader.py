from importlib import import_module
from inspect import isclass
import os
from os import walk
from os.path import abspath, basename, dirname, join
from sys import modules

from src.data_generator.extractors.base_extractor import BaseExtractor


__all__ = ('load_extractors',)

PROJ_DIR = abspath(join(dirname(abspath(__file__)), '../../..'))
PROJ_MODULE = basename(PROJ_DIR)
CURR_DIR = os.path.join(PROJ_DIR, 'data_generator', 'extractors')
CURR_MODULE = basename(CURR_DIR)
EXTRACTOR_TYPES = [
    'pse',
    'producers',
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


def is_extractor(item):
    return isclass(item) and issubclass(item, BaseExtractor)


def get_extractors(extractor_type):
    return dynamic_loader(extractor_type, is_extractor)


def load_extractors():
    extractors = dict()
    for extractor_type in EXTRACTOR_TYPES:
        for extractor in get_extractors(extractor_type):
            setattr(modules[__name__], extractor.__name__, extractor)
            extractors[extractor.__name__] = extractor
    return extractors
