# coding : utf-8

import sys
import copy
import functools
import itertools
import numpy as np
import operator
import pandas as pd
import pathlib as pl
from src import common_utils as cu
from src.parameters import (linebreaker, dir_separator, IOT_balance_tolerance)
from typing import (Any, Dict, List, Iterator, Tuple, Union)

Coordinates = Tuple[List[str], List[str]]


def read_table(IOT_file_path: pl.Path, **kwargs) -> pd.DataFrame:
    read_table = pd.read_csv(IOT_file_path,
                             index_col=0,
                             **kwargs)
    if read_table.empty:
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in " +
                         str(IOT_file_path) + linebreaker)
    return read_table


def get_header_from(IOT: pd.DataFrame) -> pd.Index:
    return IOT.columns


def get_headers_from(IOT: pd.DataFrame) -> List[pd.Index]:
    return [IOT.index, IOT.columns]


def get_filename_from(path: pl.Path):
    return path.name


def read_activities_mapping(mapping_path: pl.Path, delimiter: str='|',
                            headers: Union[List[List[str]], None] = None
                            ) -> Dict[str, List[str]]:
    """ Hypothesis : in first column are the names of the activities and in columns aggregates names """
    mapping_raw_data = cu._read_csv(mapping_path, delimiter)
    read_mapping = extract_activities_mapping(mapping_raw_data, mapping_path)
    if headers:
        read_mapping = _change_activities_order_in(read_mapping, headers)
    return read_mapping


def extract_activities_mapping(activities_mapping: Iterator[List[str]],
                               mapping_filpath : str,
                               col: Union[int, None]=None
                               ) -> Dict[str, List[str]]:
    read_mapping = dict()
    for activity_description in activities_mapping:
        activity = activity_description[0]
        if col is None:
            categories = activity_description[1:]
        else:
            categories = [activity_description[col]]
        # categories, duplicates = cu.filter_list_duplicate(categories)
        # ipdb.set_trace()
        # if duplicates:
        #     cu.raise_if_duplicates(duplicates, mapping_filpath)
        for category in categories:
                read_mapping.setdefault(category, list()).append(activity)
    return read_mapping


def _change_activities_order_in(input_mapping: List[List[str]],
                                reference_headers: List[List[str]]
                                ) -> List[List[str]]:
    reordered_mapping = dict()
    for category, activities in input_mapping.items():
        reordered_mapping[category] = _get_and_change_order_of(activities,
                                                               reference_headers)
    return reordered_mapping


def _get_and_change_order_of(activities: List[str],
                             reference_headers: List[List[str]]
                             ) -> List[str]:
    reference_header = _get_matching_header_for(activities, reference_headers)
    return _change_order_of(activities, reference_header)


def _get_matching_header_for(unordered_activities: List[str],
                             headers: List[pd.Index]
                             ) -> List[str]:
    return max(headers,
               key=lambda header: len(np.intersect1d(unordered_activities, header)))


def _change_order_of(unordered_activities: List[str],
                     header: pd.Index):
    return sorted(unordered_activities,
                  key=lambda individual: list(header).index(individual))


def read_categories_coordinates(mapping_path: pl.Path, delimiter='|'
                                ) -> Dict[str, List[str]]:
    mapping_raw_data = _read_csv(mapping_path, delimiter)
    read_mapping = _map_categories_to_coordinates(mapping_raw_data)
    return read_mapping


def _map_categories_to_coordinates(coordinates_mapping: Iterator[List[str]]
                                   ) -> Dict[str, List[str]]:
    read_mapping = dict()
    for row in coordinates_mapping:
        category = row[0]
        if category not in read_mapping:
            read_mapping[row[0]] = row[1:]
        else:
            sys.stderr.write("Warning : attempt to redefine " + category +
                             " check file" + linebreaker)
    return read_mapping


def extract_IOTs_from(IOT: pd.DataFrame,
                      activities_coordinates_mapping: Dict[str, List[str]]
                      ) -> Dict[str, Coordinates]:
    extracted_IOTs = dict()
    for category, activities_coordinates in activities_coordinates_mapping.items():
        extracted_IOTs[category] = _slice_activities(IOT, activities_coordinates)
    return extracted_IOTs


def _slice_activities(IOT: pd.DataFrame,
                      activities_coordinates: List[List[str]]
                     ) -> pd.DataFrame:
    _check_coordinates_in_IOT(IOT, activities_coordinates)
    sliced_IOT = IOT.loc[activities_coordinates]
    return sliced_IOT


def _check_coordinates_in_IOT(IOT: pd.DataFrame,
                              coordinates: Coordinates) -> None:
    IOT_headers = get_headers_from(IOT)
    IOT_headers_name = ['index', 'columns']
    for positional_arg, positional_coordinates in enumerate(coordinates):
        wrong_activities = [activity for activity in positional_coordinates if
                            activity not in IOT_headers[positional_arg]]
        if any(wrong_activities):
            sys.stderr.write("Warning : wrong coordinates" + linebreaker +
                             ', '.join(wrong_activities) + " not in " +
                             IOT_headers_name[positional_arg] + linebreaker)


def map_categories_to_activities_coordinates(category_coordinates_mapping: Dict[str, List[str]],
                                             activities_mapping: Dict[str, List[str]]
                                             ) -> Dict[str, Coordinates]:
    activities_coordinates = dict()
    for category, categories_coordinates in category_coordinates_mapping.items():
        activities_coordinates[category] = tuple(_map_values_to_list(categories_coordinates,
                                                                     activities_mapping))
    return activities_coordinates


def _map_values_to_list(input_list: List[str],
                        mapping_dictionary: Dict[str, List[str]]
                        ) -> List[List[str]]:
    surplus_headers = _check_values_in_dict(input_list, mapping_dictionary)
    if surplus_headers:
        input_list = filter_list(input_list, surplus_headers)
    output_list = list()
    for element_key in input_list:
        output_list.append(mapping_dictionary[element_key])
    return output_list


def filter_list(input_list: List,
                exclude_list: List
                ) -> List:
    output_list = list()
    for element in input_list:
        if element not in exclude_list:
            output_list.append(element)
    return output_list


def _check_values_in_dict(interest_values: List[str],
                          comparison_dictionary: Dict[str, Any]
                          ) -> List[str]:
    surplus_headers = set(interest_values) - set(comparison_dictionary.keys())
    if surplus_headers:
        sys.stderr.write("Warning : " + ", ".join(surplus_headers) + " not in mapping" + linebreaker)
    return list(surplus_headers)


def disaggregate_in_coordinates(coordinates_mapping: Dict[str, Coordinates],
                                to_expand_categories: List[str],
                                reference_category: List[str]) -> Dict[str, Coordinates]:
    new_coordinates_mapping = copy.deepcopy(coordinates_mapping)
    for to_expand_category in to_expand_categories:
        new_coordinates_mapping.update(_disaggregate_coordinates(coordinates_mapping[to_expand_category],
                                                                 coordinates_mapping[reference_category]))
    return new_coordinates_mapping


def _disaggregate_coordinates(to_expand_coordinates, reference_coordinates):
    different_index = _get_dissimilar_coordinates_index(to_expand_coordinates, reference_coordinates)
    output_grouping = dict()
    for activity in to_expand_coordinates[different_index]:
        new_nested_headers = list(copy.deepcopy(reference_coordinates))
        new_nested_headers[different_index] = [activity]
        output_grouping[activity] = tuple(new_nested_headers)
    return output_grouping


def _get_dissimilar_coordinates_index(working_coordinates, reference_coordinates):
    for index, positional_coordinates in enumerate(reference_coordinates):
        if working_coordinates[index] != positional_coordinates:
            return index


def get_ERE(use_categories: List[str], ressource_categories: List[str],
            IOT: pd.DataFrame, coordinates_mapping: Dict[str, List[List[str]]]) -> pd.Series:
    ressources = functools.reduce(operator.add, map(lambda category: row_sum(_slice_activities(IOT,
                                                                                               coordinates_mapping[category])),
                                                    ressource_categories))
    uses = functools.reduce(operator.add, map(lambda category: col_sum(_slice_activities(IOT,
                                                                                         coordinates_mapping[category])),
                                              use_categories))
    return uses - ressources


def row_sum(IOT: pd.DataFrame) -> pd.Series:
    return IOT.sum(axis=0)


def col_sum(IOT: pd.DataFrame) -> pd.Series:
    return IOT.sum(axis=1)


def is_ERE_balanced(ERE: pd.Series):
    is_balanced = abs(ERE) < IOT_balance_tolerance
    if not all(is_balanced):
        sys.stderr.write("Warning : unbalanced IOT" + linebreaker +
                         ', '.join(ERE.index[~is_balanced]) + linebreaker)


def is_IOT_balanced(use_categories: List[str], ressource_categories: List[str],
                    IOT: pd.DataFrame, coordinates_mapping: Dict[str, List[List[str]]]):
    ERE = get_ERE(use_categories, ressource_categories, IOT, coordinates_mapping)
    is_ERE_balanced(ERE)


def modify_activity_value(IOT, coordinates: Coordinates,
                          condition: Union[pd.DataFrame, pd.Series],
                          fill_values: Union[pd.DataFrame, pd.Series]):
    IOT.update(IOT.loc[coordinates].where(~condition, fill_values))


def read_list(path: str, delimiter: str=',') -> List[str]:
    iter_raw_data = _read_csv(path, delimiter)
    return list(itertools.chain.from_iterable(iter_raw_data))


def extract_accounts(data_account: pd.DataFrame) -> Dict[str, pd.Series]:
    output_data_account = dict()
    for account in data_account.index:
        output_data_account[account] = data_account.loc[account, ]
    return output_data_account


def extract_households_accounts(data_account: pd.DataFrame, to_extract_accounts: List[str]
                                ) -> Dict[str, float]:
    return extract_table_variables(data_account.apply(abs), to_extract_accounts, 'Households')


def extract_table_variables(table: pd.DataFrame, to_extract_variables: List[str],
                            interest_variable: str) -> Dict[str, float]:
    output_variables = dict()
    for to_extract_variable in to_extract_variables:
        output_variables[to_extract_variable] = table.loc[to_extract_variable, interest_variable]
    return output_variables


def map_list_to_dict(interest_list: List[str],
                     mapping_dictionary: Dict[str, Any]
                     ) -> Dict[str, Any]:
    surplus_headers = _check_values_in_dict(interest_list, mapping_dictionary)
    if surplus_headers:
        interest_list = filter_list(interest_list, surplus_headers)
    output_dict = dict()
    for interest_var in interest_list:
        output_dict[interest_var] = mapping_dictionary[interest_var]
    return output_dict


# def _to_list_iter(entry: Any) -> Any:
#     if not hasattr(entry, '__iter__'):
#         return iter([entry])
#     return iter(entry)


# def remap_dict(entry_dict: Dict[str, Any],
#                remapping_dict: Dict[Any, Any],
#                keep=False) -> Dict[str, Any]:
#     if not keep:
#         _ = _check_values_in_dict(entry_dict.values(), remapping_dict)
#     remapped_dict = dict()
#     for entry_key, entry_value in entry_dict.items():
#         try:
#             remapped_dict[entry_key] = remapping_dict[entry_value]
#         except KeyError:
#             if keep:
#                 remapped_dict[entry_key] = entry_value
#             else:
#                 pass
#     return remapped_dict


# def filter_dict(input_dict: Dict[str, Any],
#                 exclude_list: List[str]
#                 ) -> Dict[str, Any]:
#     output_dict = copy.deepcopy(input_dict)
#     for element_to_exclude in exclude_list:
#         del output_dict[element_to_exclude]
#     return output_dict
