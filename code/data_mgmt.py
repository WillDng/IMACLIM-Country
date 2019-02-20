# coding : utf-8

import os
import sys
import collections
import copy
import csv
import functools
import numpy as np
import pandas

linebreaker = '\n'
dir_separator = os.sep

def read_IOT(IOT_file_path, **kwargs):
    read_IOT = pandas.read_csv(IOT_file_path, 
                               index_col=0,
                               **kwargs)
    if read_IOT.empty:
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in "+get_filename_from(IOT_file_path)+linebreaker)
    return read_IOT

def get_header_from(IOT):
    return IOT.columns

def get_headers_from(IOT):
    return [IOT.index, IOT.columns]

def get_filename_from(path):
    return path.split(dir_separator)[-1]

def read_activities_category_mapping(mapping_path, delimiter='|', headers=None):
    """ Hypothesis : in first column are the names of the activities and in columns aggregates names """
    reader = _get_reader_from(mapping_path, delimiter)
    read_mapping = collections.defaultdict(list)
    for activity_description in reader:
        activity = activity_description[0]
        categories = activity_description[1:]
        if not categories:
            sys.stderr.write("Warning : delimiter might not be correctly informed in read_activities_category_mapping() for "+get_filename_from(mapping_path)+linebreaker)
            return            
        for category in categories:
            if activity not in read_mapping[category]:
                read_mapping[category].append(activity)
            else:
                pass
                #FIXME should raise warning ?
    if headers:
        read_mapping = _change_activities_order_in(read_mapping, headers)
    return read_mapping

def _get_reader_from(path, delimiter):
    return csv.reader(open(path), delimiter=delimiter)

def _change_activities_order_in(input_mapping, reference_headers):
    reordered_mapping = dict()
    for category, activities in input_mapping.items():
        reordered_mapping[category] = _get_and_change_order_of(activities, reference_headers)
    return reordered_mapping

def _get_and_change_order_of(activities, reference_headers):
    reference_header = _get_matching_header_for(activities, reference_headers)
    return _change_order_of(activities, reference_header)

def _get_matching_header_for(unordered_activities, headers):
    return max(headers, key=lambda header: len(np.intersect1d(unordered_activities, header)))

def _change_order_of(unordered_activities, header):
    return sorted(unordered_activities, key=lambda individual:list(header).index(individual))

def read_categories_coordinates_mapping(mapping_path, delimiter='|'):
    reader = _get_reader_from(mapping_path, delimiter)
    read_mapping = dict()
    for row in reader:
        category = row[0]
        if category not in read_mapping:
            read_mapping[row[0]] = row[1:]
        else:
            sys.stderr.write("Warning : "+category+" already in categories coordinates mapping, check file at "+mapping_path+linebreaker)
    return read_mapping

def extract_IOTs_from(IOT, activities_category_mapping):
    extracted_IOTs = dict()
    for var_name, field_header in activities_category_mapping.items():
        extracted_IOTs[var_name] = _slice(IOT, field_header)
    return extracted_IOTs

def map_category_to_activities(grouping, activities_mapping):
    expanded_grouping = dict()
    for group_name, groups in grouping.items():
        expanded_grouping[group_name] = _map_aggregate_to_activities(groups, activities_mapping)
    return expanded_grouping

def _map_aggregate_to_activities(groups, activities_mapping):
    return list(map(lambda aggregate:activities_mapping[aggregate], groups))    

def _slice(IOT, field_headers):
    sliced_IOT = IOT.loc[tuple(field_headers)]
    if sliced_IOT.isnull().values.any():
        sys.stderr.write("Warning : IOT activities coordinates might be ill informed"+linebreaker)
    return sliced_IOT

to_expand_variables = ['FC', 'OthPart_IOT']
reference_variable = 'IC'

def disaggregate_in_coordinates_category_mapping(coordinates_category_mapping):
    new_coordinates_category_mapping = copy.deepcopy(coordinates_category_mapping)
    for to_expand_variable in to_expand_variables:
        new_coordinates_category_mapping.update(_disaggregate_coordinates(coordinates_category_mapping[to_expand_variable], 
                                                                                          coordinates_category_mapping[reference_variable]))
    return new_coordinates_category_mapping

def _disaggregate_coordinates(to_expand_coordinates, reference_coordinates):
    different_index = _get_dissimilar_coordinates_index(to_expand_coordinates, reference_coordinates)
    output_grouping = dict()
    for individual in to_expand_coordinates[different_index]:
        new_nested_headers = copy.deepcopy(reference_coordinates)
        new_nested_headers[different_index] = [individual]
        output_grouping[individual] = new_nested_headers
    return output_grouping

def _get_dissimilar_coordinates_index(working_coordinates, reference_coordinates):
    for index, positional_list in enumerate(reference_coordinates):
        if working_coordinates[index] != positional_list:
            return index

balance_tolerance = 1E-2

def check_use_ressource(IOT, headers_grouping, use_headers, ressource_headers, tolerance=balance_tolerance):
    use_headers = _combine_category_coordinates(use_headers, headers_grouping, get_headers_from(IOT))
    ressource_headers = _combine_category_coordinates(ressource_headers, headers_grouping, get_headers_from(IOT))
    uses = _slice(IOT, use_headers).sum()
    ressources = _slice(IOT, ressource_headers).sum(axis=1)
    balances = uses - ressources < tolerance
    if not all(balances):
        sys.stderr.write("Warning : unbalanced IOT"+linebreaker)
        sys.stderr.write(', '.join([activities for activities, balanced in zip(use_headers[0], balances) if not balanced])+linebreaker)

def _combine_category_coordinates(category_to_combine, activities_coordinates_category_mapping, reference_headers):
    expanded_headers = _map_aggregate_to_activities(category_to_combine, activities_coordinates_category_mapping)
    expanded_merged_headers = functools.reduce(_merge_headers, expanded_headers)
    return list(map(lambda positional_header: _get_and_change_order_of(positional_header, reference_headers), expanded_merged_headers))

def _merge_headers(first_header, second_header):
    merged_headers = list()
    for first_positional_header, second_positional_header in zip(first_header, second_header):
        merged_headers.append(list(set(first_positional_header+second_positional_header)))
    return merged_headers