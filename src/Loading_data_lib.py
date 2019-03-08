# coding : utf-8

import sys
import collections
import copy
import csv
import functools
import itertools
import numpy as np
import operator
import pandas as pd
from parameters import (linebreaker, dir_separator, IOT_balance_tolerance)
from typing import (Any, Dict, List, Iterable, Tuple, Union)

Coordinates = Tuple[List[str], List[str]]


def read_table(IOT_file_path, **kwargs):
    read_table = pd.read_csv(IOT_file_path,
                             index_col=0,
                             **kwargs)
    if read_table.empty:
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in " +
                         get_filename_from(IOT_file_path) + linebreaker)
    return read_table


def get_header_from(IOT):
    return IOT.columns


def get_headers_from(IOT):
    return [IOT.index, IOT.columns]


def get_filename_from(path):
    return path.split(dir_separator)[-1]


def read_activities_mapping(mapping_path: str, delimiter='|',
                            headers: List[List[str]] = None) -> Dict[str, List[str]]:
    """ Hypothesis : in first column are the names of the activities and in columns aggregates names """
    mapping_raw_data = _read_csv(mapping_path, delimiter)
    read_mapping = _aggregate_activities(mapping_raw_data)
    if headers:
        read_mapping = _change_activities_order_in(read_mapping, headers)
    return read_mapping


def _aggregate_activities(activities_mapping: Iterable[List[str]]) -> Dict[str, List[str]]:
    read_mapping = collections.defaultdict(list)
    for activity_description in activities_mapping:
        activity, categories = activity_description[0], activity_description[1:]
        for category in categories:
            if activity not in read_mapping[category]:
                read_mapping[category].append(activity)
            else:
                pass
                # FIXME should raise warning ?
    return dict(read_mapping)


def _read_csv(path: str, delimiter: str) -> Iterable[List[str]]:
    mapping_raw_data = list(csv.reader(open(path), delimiter=delimiter))
    _warns_if_bad_delimiter(mapping_raw_data, path)
    return iter(_remove_trailing_blanks(mapping_raw_data))


def _warns_if_bad_delimiter(file_content: List[List[str]], file_path: str):
    callers_caller = sys._getframe(3).f_code.co_name
    if len(file_content[0]) == 1:
        sys.stderr.write("Warning : delimiter might not be correctly informed in " +
                         callers_caller + "() for " + get_filename_from(file_path) +
                         linebreaker)


def _remove_trailing_blanks(file_content: List[List[str]]):
    clean_file_content = list()
    for row in file_content:
        clean_file_content.append(list(filter(None, row)))
    return clean_file_content


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


def read_categories_coordinates(mapping_path, delimiter='|'
                                ) -> Dict[str, List[str]]:
    mapping_raw_data = _read_csv(mapping_path, delimiter)
    read_mapping = _map_categories_to_coordinates(mapping_raw_data)
    return read_mapping


def _map_categories_to_coordinates(coordinates_mapping: Iterable[List[str]]
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


def extract_IOTs_from(IOT, activities_coordinates_mapping):
    extracted_IOTs = dict()
    for category, activities_coordinates in activities_coordinates_mapping.items():
        extracted_IOTs[category] = _slice_activities(IOT, activities_coordinates)
    return extracted_IOTs


def _slice_activities(IOT, activities_coordinates: List[List[str]]):
    _check_coordinates_in_IOT(IOT, activities_coordinates)
    sliced_IOT = IOT.loc[activities_coordinates]
    return sliced_IOT


def _check_coordinates_in_IOT(IOT, coordinates: List[List[str]]):
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
    _check_values_in_dict(input_list, mapping_dictionary)
    output_list = list()
    for element_key in input_list:
        try:
            output_list.append(mapping_dictionary[element_key])
        except KeyError:
            # FIXME redundancy with previous check
            pass
    return output_list


def _check_values_in_dict(interest_values: List[str],
                          comparison_dictionary: Dict[str, Any]):
    absent_headers = set(interest_values) - set(comparison_dictionary.keys())
    if absent_headers:
        sys.stderr.write("Warning : " + ", ".join(absent_headers) + " not in mapping" + linebreaker)


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


def read_list(path: str, delimiter=',') -> List[str]:
    list_raw_data = _read_csv(path, delimiter)
    return list(itertools.chain.from_iterable(list_raw_data))


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
    _check_values_in_dict(interest_list, mapping_dictionary)
    output_dict = dict()
    for interest_var in interest_list:
        try:
            output_dict[interest_var] = mapping_dictionary[interest_var]
        except KeyError:
            # FIXME : redundant problem with _map_values_to_list()
            pass
    return output_dict
