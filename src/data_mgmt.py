# coding : utf-8

from typing import Dict, List
import sys
import collections
import copy
import csv
import functools
import numpy as np
import operator
import pandas as pd
from parameters import (linebreaker, dir_separator, IOT_balance_tolerance)


def read_IOT(IOT_file_path, **kwargs):
    read_IOT = pd.read_csv(IOT_file_path,
                           index_col=0,
                           **kwargs)
    if read_IOT.empty:
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in " +
                         get_filename_from(IOT_file_path) + linebreaker)
    return read_IOT


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


def _aggregate_activities(activities_mapping: List[List[str]]) -> Dict[str, List[str]]:
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


def _read_csv(path: str, delimiter: str) -> List[List[str]]:
    mapping_raw_data = list(csv.reader(open(path), delimiter=delimiter))
    _warns_if_bad_delimiter(mapping_raw_data, path)
    return mapping_raw_data


def _warns_if_bad_delimiter(file_content: List[List], file_path: str):
    callers_caller = sys._getframe(3).f_code.co_name
    if len(file_content[0]) == 1:
        sys.stderr.write("Warning : delimiter might not be correctly informed in " +
                         callers_caller + "() for " + get_filename_from(file_path) +
                         linebreaker)


def _change_activities_order_in(input_mapping: List[List[str]], reference_headers: List[List[str]]) -> List[List[str]]:
    reordered_mapping = dict()
    for category, activities in input_mapping.items():
        reordered_mapping[category] = _get_and_change_order_of(activities,
                                                               reference_headers)
    return reordered_mapping


def _get_and_change_order_of(activities: List[str], reference_headers: List[List[str]]) -> List[str]:
    reference_header = _get_matching_header_for(activities, reference_headers)
    return _change_order_of(activities, reference_header)


def _get_matching_header_for(unordered_activities: List[str], headers: List[List[str]]) -> List[str]:
    return max(headers,
               key=lambda header: len(np.intersect1d(unordered_activities, header)))


def _change_order_of(unordered_activities, header):
    return sorted(unordered_activities,
                  key=lambda individual: list(header).index(individual))


def read_categories_coordinates_mapping(mapping_path, delimiter='|'):
    mapping_raw_data = _read_csv(mapping_path, delimiter)
    read_mapping = _map_categories_to_coordinates(mapping_raw_data)
    return read_mapping


def _map_categories_to_coordinates(coordinates_mapping: Dict[str, List[str]]) -> Dict[str, List[str]]:
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
    sliced_IOT = IOT.loc[tuple(activities_coordinates)]
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


def map_categories_to_activities_coordinates(category_coordinates_mapping,
                                             activities_mapping):
    activities_coordinates = dict()
    for category, categories_coordinates in category_coordinates_mapping.items():
        activities_coordinates[category] = _map_values_to_list(categories_coordinates,
                                                               activities_mapping)
    return activities_coordinates


def _map_values_to_list(input_list, mapping_dictionary):
    output_list = list()
    for element_key in input_list:
        try:
            output_list.append(mapping_dictionary[element_key])
        except KeyError:
            sys.stderr.write(element_key + " not in mapping, please check")
    return output_list


def disaggregate_in_coordinates_mapping(coordinates_mapping, to_expand_categories, reference_category):
    new_coordinates_mapping = copy.deepcopy(coordinates_mapping)
    for to_expand_category in to_expand_categories:
        new_coordinates_mapping.update(_disaggregate_coordinates(coordinates_mapping[to_expand_category],
                                                                 coordinates_mapping[reference_category]))
    return new_coordinates_mapping


def _disaggregate_coordinates(to_expand_coordinates, reference_coordinates):
    different_index = _get_dissimilar_coordinates_index(to_expand_coordinates, reference_coordinates)
    output_grouping = dict()
    for individual in to_expand_coordinates[different_index]:
        new_nested_headers = copy.deepcopy(reference_coordinates)
        new_nested_headers[different_index] = [individual]
        output_grouping[individual] = new_nested_headers
    return output_grouping


def _get_dissimilar_coordinates_index(working_coordinates, reference_coordinates):
    for index, positional_coordinates in enumerate(reference_coordinates):
        if working_coordinates[index] != positional_coordinates:
            return index

# def check_use_ressource(IOT, activities_coordinates_mapping, use_categories,
#                         ressource_categories, balance_tolerance):
#     use_activities_coordinates, ressource_activities_coordinates = map(lambda categories_list: _combine_category_coordinates(categories_list,
#                                                                                                           activities_coordinates_mapping,
#                                                                                                           get_headers_from(IOT)),
#                                                                        [use_categories, ressource_categories])
#     difference = get_use_ressource_difference(IOT, use_activities_coordinates, ressource_activities_coordinates)
#     is_balanced =  difference < balance_tolerance
#     if not all(is_balanced):
#         studied_activities = list(_combine_category_coordinates(use_categories, activities_coordinates_mapping, get_headers_from(IOT)))[0]
#         sys.stderr.write("Warning : unbalanced IOT"+
#                          linebreaker+
#                          ', '.join([activities for activities, balanced in \
#                                     zip(studied_activities, is_balanced) \
#                                     if not balanced])+
#                          linebreaker)


# def get_use_ressource_difference(IOT, use_activities_coordinates, ressource_activities_coordinates):
#     use_ressource_sum = _slice_and_sum(use_activities_coordinates, ressource_activities_coordinates, IOT)
#     difference = functools.reduce(operator.sub, use_ressource_sum)
#     return difference


# def _combine_category_coordinates(category_to_combine,
#                                   activities_coordinates_mapping,
#                                   IOT_headers):
#     activities_coordinates_to_combine = _map_values_to_list(category_to_combine,
#                                                             activities_coordinates_mapping)
#     merged_activities_coordinates = functools.reduce(_merge_coordinates,
#                                                      activities_coordinates_to_combine)
#     return map(lambda positional_coordinate: _get_and_change_order_of(positional_coordinate,
#                                                                       IOT_headers),
#                merged_activities_coordinates)


# def _slice_and_sum(use_activities_coordinates, ressource_activities_coordinates, IOT):
#     use_ressource_sum = list()
#     for axis_index, activities_coordinates in enumerate([use_activities_coordinates, ressource_activities_coordinates]):
#         use_ressource_sum.append(_slice_activities(IOT, activities_coordinates).sum(axis=axis_index))
#     return use_ressource_sum


# def _merge_coordinates(first_coordinates, second_coordinates):
#     merged_coordinates = list()
#     for first_positional_coordinate, second_positional_coordinate in zip(first_coordinates, second_coordinates):
#         merged_coordinates.append(list(set(first_positional_coordinate +
#                                            second_positional_coordinate)))
#     return merged_coordinates


def slice_and_sum(IOT: pd.DataFrame, activities_coordinates: List[List[str]], axis=0):
    sliced_IOT = _slice_activities(IOT, activities_coordinates)
    return sliced_IOT.sum(axis=axis)


def get_ERE(use_categories: List[str], ressource_categories: List[str],
            IOT: pd.DataFrame, coordinates_mapping: Dict[str, List[List[str]]]) -> pd.Series:
    # temp = map(lambda category: slice_and_sum(IOT,
    #                                           coordinates_mapping[category]),
    #            use_categories)
    uses = functools.reduce(operator.add, map(lambda category: slice_and_sum(IOT,
                                                                             coordinates_mapping[category]),
                                              use_categories))
    ressources = functools.reduce(operator.add, map(lambda category: slice_and_sum(IOT,
                                                                                   coordinates_mapping[category],
                                                                                   axis=1),
                                                    ressource_categories))
    return ressources - uses


def is_ERE_balanced(ERE: pd.Series):
    is_balanced = abs(ERE) < IOT_balance_tolerance
    if not all(is_balanced):
        sys.stderr.write("Warning : unbalanced IOT" + linebreaker +
                         ', '.join(ERE.index[~is_balanced]) + linebreaker)


def is_IOT_balanced(use_categories: List[str], ressource_categories: List[str],
                    IOT: pd.DataFrame, coordinates_mapping: Dict[str, List[List[str]]]):
    ERE = get_ERE(use_categories, ressource_categories, IOT, coordinates_mapping)
    is_ERE_balanced(ERE)
