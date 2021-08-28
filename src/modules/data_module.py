"""
this module provides interfaces for working with data
"""
from __future__ import annotations

import json
from collections import OrderedDict
from typing import Callable, Iterable


class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory: Callable = None, *args, **kwargs):
        if (default_factory is not None and
                not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


def filter_by_year(data: dict, year: int) -> dict:
    """
    this function takes the meta data as input and only return the locations containing data for the specifies year.
    if location contains multiple dataframes, only the dataframes remain in the dict that are valid for the specified
    year, all other dataframes will be removed

    Parameters
    ----------
    data : dict
        the data in the format specified in meta.schema.json. this wont be modified
    year : int
        the year to filter for

    Returns
    -------
    dict :
        a new dict only containing the filtered data

    See Also
    --------
    filter_by_category : filter the data by category
    """
    filtered_data = data | {"places": []}

    for place in data["places"]:
        dataframes = []

        for dataframe in place["data"]:
            if dataframe["startYear"] <= year <= dataframe["endYear"]:
                dataframes.append(dataframe)

        if dataframes:
            filtered_data["places"].append(
                place | {"data": dataframes}
            )

    return filtered_data


def get_categories(data: dict) -> set[str]:
    """
    this function return all categories that are in a given dataset

    Parameters
    ----------
    data : dict
        all unique categories in this dataset will be returned

    Returns
    -------
    set :
        a set of unique categories
    """
    categories = set()
    for place in data["places"]:
        categories.update(category for category in place["category"])
    return categories


def filter_by_category(data: dict, category: str, match_category: Callable[[Iterable], bool] = any) -> dict:
    """
    this function takes the meta data as input and only returns the locations that matches a a given category.

    Parameters
    ----------
    data : dict
        the data in the format specified in meta.schema.json. this wont be modified
    category : str
        the data will be filtered by this. multiple categories can be specified
    match_category : {any, all}, optional, default=any
        this controls how multiple specified categories are handled. if this is 'any' the location will be included
        in the filtered data as long one of the specified categories matches the location. if it is 'all', all the
        specified categories must match the location

    Returns
    -------
    dict :
        a new dict only containing the filtered data

    See Also
    --------
    filter_by_year : filters the data by year
    """

    filtered_data = data | {"places": []}

    for place in data["places"]:
        if match_category(cat in place["category"] for cat in category):
            filtered_data["places"].append(place)

    return filtered_data


def pprint_dict(dct: dict) -> None:
    """
    prints a dict nicely formatted to the console

    Parameters
    ----------
    dct: dict
        will be printed
    """
    print(json.dumps(dct, indent=4, ensure_ascii=False))
