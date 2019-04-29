# coding : utf-8

import sys
import copy
import functools
import itertools
import numpy as np
import operator
import pandas as pd
import pathlib as pl
from src import (common_utils as cu,
                 Households_disag as hhd)
from src.parameters import (linebreaker, IOT_balance_tolerance)
from typing import (Any, Dict, List, Iterator, Tuple, Union)


Coordinates = Tuple[List[str], List[str]]


def get_header_from(IOT: pd.DataFrame) -> pd.Index:
    return IOT.columns


def get_headers_from(IOT: pd.DataFrame) -> List[pd.Index]:
    return [IOT.index, IOT.columns]


def get_filename_from(path: pl.Path):
    return path.name


def read_activities_mapping(mapping_path: pl.Path, delimiter: str = '|',
                            headers: Union[List[List[str]], None] = None
                            ) -> Dict[str, Dict[str, List[str]]]:
    """ Hypothesis : in first column are the names of the activities and in columns aggregates names """
    mapping_raw_data = cu._read_csv(mapping_path,
                                    delimiter,
                                    remove_blanks=False)
    file_header = list(filter(None, mapping_raw_data.__next__()))
    mapping_raw_data = list(mapping_raw_data)
    activities_mapping = dict()
    for grouping_index, grouping_name in enumerate(file_header):
        read_mapping = cu.extract_aggregation_mapping(mapping_raw_data,
                                                      col=grouping_index + 1)
        if read_mapping.get('', None):
            del read_mapping['']
        if headers:
            read_mapping = _change_activities_order_in(read_mapping, headers)
        activities_mapping[grouping_name] = read_mapping
    return activities_mapping


def change_activities_mapping_order(activities_mapping: Dict[str, Dict[str, List[str]]],
                                    headers: List[List[str]]
                                    ) -> Dict[str, Dict[str, List[str]]]:
    changed_activities_mappping = dict()
    for grouping_name, grouping_mapping in activities_mapping.items():
        changed_activities_mappping[grouping_name] = _change_activities_order_in(grouping_mapping,
                                                                                 headers)
    return changed_activities_mappping


def _change_activities_order_in(input_mapping: Dict[str, List[str]],
                                reference_headers: List[List[str]]
                                ) -> Dict[str, List[str]]:
    reordered_mapping = dict()
    for category, activities in input_mapping.items():
        reordered_mapping[category] = _get_and_change_order_of(activities,
                                                               reference_headers)
    return reordered_mapping


def _get_and_change_order_of(activities: List[str],
                             reference_headers: List[List[str]]
                             ) -> List[str]:
    reference_header = get_matching_header_for(activities, reference_headers)
    return change_order_of(activities, reference_header)


def get_matching_header_for(unordered_activities: List[str],
                            headers: List[pd.Index]
                            ) -> List[str]:
    return max(headers,
               key=lambda header: len(np.intersect1d(unordered_activities, header)))


def change_order_of(unordered_activities: List[str],
                    header: pd.Index):
    header = list(header)
    return sorted(unordered_activities,
                  key=lambda individual: header.index(individual))


def read_categories_coordinates(mapping_path: pl.Path, delimiter='|'
                                ) -> Dict[str, List[str]]:
    mapping_raw_data = cu._read_csv(mapping_path, delimiter)
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


def read_list(path: str, delimiter: str = ','
              ) -> List[str]:
    iter_raw_data = cu._read_csv(path, delimiter)
    return list(itertools.chain.from_iterable(iter_raw_data))


def extract_accounts(account_table: pd.DataFrame,
                     to_modify_accounts: Dict[str, str]
                     ) -> Dict[str, Union[pd.Series, float]]:
    extracted_accounts = extract_all_accounts(account_table)
    modified_accounts = extract_selected_accounts(account_table.apply(abs),
                                                  to_modify_accounts)
    extracted_accounts.update(modified_accounts)
    return extracted_accounts


def extract_all_accounts(account_table: pd.DataFrame
                         ) -> Dict[str, pd.Series]:
    output_data_account = dict()
    for account in account_table.index:
        output_data_account[account] = account_table.loc[account, ]
    return output_data_account


def extract_selected_accounts(account_table: pd.DataFrame,
                              to_modify_accounts: Dict[str, str],
                              ) -> Dict[str, Union[pd.Series, float]]:
    to_pick_accounts, to_trim_accounts = filter_accounts_type(to_modify_accounts)
    picked_accounts = pick_selection(account_table, to_pick_accounts)
    trimmed_accounts = trim_selected_accounts(account_table, to_trim_accounts)
    return dict(picked_accounts, **trimmed_accounts)


def filter_accounts_type(to_modify_accounts: Dict[str, str]
                         ) -> (Dict[str, str], Dict[str, str]):
    to_pick_accounts = copy.deepcopy(to_modify_accounts)
    to_trim_accounts = dict()
    to_delete_marker = '  '
    for to_modify_account, account_category in to_modify_accounts.items():
        if ((isinstance(account_category, str)) and
            (account_category.startswith(to_delete_marker))):
            to_trim_accounts[to_modify_account] = account_category.lstrip(to_delete_marker)
            del to_pick_accounts[to_modify_account]
    return to_pick_accounts, to_trim_accounts


def pick_selection(table: pd.DataFrame,
                   to_pick_variables: Dict[str, str]
                   ) -> Dict[str, float]:
    picked_variables = dict()
    for to_pick_line, to_pick_column in to_pick_variables.items():
        picked_variables[to_pick_line] = table.loc[to_pick_line, to_pick_column]
    return picked_variables


def trim_selected_accounts(account_table: pd.DataFrame,
                           to_trim_accounts: Dict[str, str]
                           ) -> Dict[str, pd.Series]:
    trimmed_accounts = dict()
    for to_trim_account, account_category in to_trim_accounts.items():
        trimmed_categories = list(account_table.columns)
        trimmed_categories.remove(account_category)
        trimmed_accounts[to_trim_account] = account_table.loc[(to_trim_account, trimmed_categories)]
    return trimmed_accounts


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


def extend_activities_mapping(to_extend_activities_mapping_path: str,
                              IOT: pd.DataFrame,
                              common_mapping: Dict[str, List[str]]):
    # FIXME delimiter is hardcoded
    new_activities_mapping = read_activities_mapping(to_extend_activities_mapping_path,
                                                     delimiter=',',
                                                     headers=get_headers_from(IOT))
    return dict(common_mapping, **cu.unpack_nested_dict(new_activities_mapping))


def get_categories_coordinates(categories_coord_path,
                               activities_mapping):
    categories_coord = read_categories_coordinates(categories_coord_path,
                                                   delimiter=',')
    return map_categories_to_activities_coordinates(categories_coord,
                                                    activities_mapping)


def normalize_row_in(table: pd.DataFrame,
                     item_normalize_onto: Union[str, None],
                     reference: pd.Series
                     ) -> pd.DataFrame:
    return hhd.normalize_column_in(table.T,
                                   item_normalize_onto,
                                   reference).T
