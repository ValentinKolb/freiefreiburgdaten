import json
from jsonschema import validate


def load_data(file: str = "data/meta.json", schema: str = "data/meta.schema.json"):
    """
    this function loads the meta.json file and validates it against the scheme

    Parameters
    ----------
    file : str
        the path of the file
    schema : str
        the path of the json scheme

    Returns
    -------
    dict :
        the parsed meta.json file as dict
    """
    with open(file) as file:
        data = json.load(file)

    with open(schema) as file:
        schema = json.load(file)

    validate(instance=data, schema=schema)

    return data


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


def pprint_dict(dct: dict) -> None:
    """
    prints a dict nicely formatted to the console

    Parameters
    ----------
    dct: dict
        will be printed
    """
    print(json.dumps(dct, indent=4))


if __name__ == '__main__':
    d = load_data(file="data/test_meta.json")
    filtered = filter_by_year(d, 2006)
    # pprint_dict(d)
    pprint_dict(filtered)
