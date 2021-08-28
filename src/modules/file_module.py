"""
this module provides interfaces for working with files
"""

import csv
import io
import json
from functools import lru_cache
from jsonschema import validate

from modules.data_module import DefaultOrderedDict


@lru_cache(maxsize=10)
def load_csv_file_cached(csv_file: str, delimiter: str = ',', encoding='utf8') -> DefaultOrderedDict[list]:
    """
    this functions loads csv data from a file. the result will be cached

    Parameters
    ----------
    csv_file : str
        the path of the file
    delimiter : str
        the delimiter used in the csv file
    encoding : str
        the csv file encoding

    Returns
    -------
    DefaultOrderedDict :
        returns the content of the csv in a dict, the headers are the keys and the corresponding values are stored
        in a list accessed by the keys
    """
    reader = csv.DictReader(
        io.StringIO(
            load_file_cached(csv_file,
                             encoding=encoding
                             )
        ),
        delimiter=delimiter
    )
    data_dict = DefaultOrderedDict(list)
    [[data_dict[key].append(value) for key, value in row.items()] for row in reader]
    return data_dict


@lru_cache(maxsize=10)
def load_file_cached(file: str, encoding='utf8') -> str:
    """
    this function loads the content of a file and caches it to reduce load times in the future

    Parameters
    ----------
    file : str
        the path of the file
    encoding : str
        the file encoding

    Returns
    -------
    str :
        the content of the file, this is only read once, the next time the result will be cached
    """
    with open(file, encoding=encoding) as file:
        return file.read()


def load_meta_data(file: str = "data/meta.json", schema: str = "data/meta.schema.json", encoding='utf8') -> dict:
    """
    this function loads the meta.json file and validates it against the scheme

    Parameters
    ----------
    file : str
        the path of the file
    schema : str
        the path of the json scheme
    encoding : str
        the file encoding

    Returns
    -------
    dict :
        the parsed meta.json file as dict
    """
    with open(file, encoding=encoding) as file:
        meta_data = json.load(file)

    with open(schema) as file:
        schema = json.load(file)

    validate(instance=meta_data, schema=schema)

    return meta_data
