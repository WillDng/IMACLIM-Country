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

def read_activities_category_mapping(activities_mapping_path, delimiter='|', headers=None):
    """ Hypothesis : in first column are the names of the activities and in columns aggregates names """
    reader = _get_reader_from(activities_mapping_path, delimiter)
    read_activities_category_mapping = collections.defaultdict(list)
    for individual_description in reader:
        individual = individual_description[0]
        aggregates = individual_description[1:]
        if not aggregates:
            sys.stderr.write("Warning : delimiter might not be correctly informed in read_activities_category_mapping() for "+get_filename_from(activities_mapping_path)+linebreaker)
            return            
        for aggregate in aggregates:
            if individual not in read_activities_category_mapping[aggregate]:
                read_activities_category_mapping[aggregate].append(individual)
            else:
                pass
                #FIXME should raise warning ?
    if headers:
        read_activities_category_mapping = _change_activities_order_in(read_activities_category_mapping, headers)
    return read_activities_category_mapping

def _get_reader_from(path, delimiter):
    return csv.reader(open(path), delimiter=delimiter)

def _change_activities_order_in(activities_category_mapping, reference_headers):
    reordered_activities_category_mapping = dict()
    for aggregate, activities in activities_category_mapping.items():
        reordered_activities_category_mapping[aggregate] = _get_and_change_order_of(activities, reference_headers)
    return reordered_activities_category_mapping

def _get_and_change_order_of(activities, reference_headers):
    reference_header = _get_matching_header_for(activities, reference_headers)
    return _change_order_of(activities, reference_header)

def _get_matching_header_for(unordered_activities, headers):
    return max(headers, key=lambda header: len(np.intersect1d(unordered_activities, header)))

def _change_order_of(unordered_activities, header):
    return sorted(unordered_activities, key=lambda individual:list(header).index(individual))

def read_category_coordinates_from(path, delimiter='|'):
    reader = _get_reader_from(path, delimiter)
    grouping = dict()
    for row in reader:
        key = row[0]
        if key not in grouping:
            grouping[row[0]] = row[1:]
        else:
            sys.stderr.write("Warning : "+key+" already in grouping, check grouping file at "+path+linebreaker)
    return grouping

def extract_IOTs_from(IOT, field_headers):
    out_IOT = dict()
    for var_name, field_header in field_headers.items():
        out_IOT[var_name] = _slice(IOT, field_header)
    return out_IOT

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
        new_coordinates_category_mapping.update(_generate_activities_in_expanded_grouping(coordinates_category_mapping[to_expand_variable], 
                                                                                          coordinates_category_mapping[reference_variable]))
    return new_coordinates_category_mapping

def _generate_activities_in_expanded_grouping(to_expand_headers, reference_headers):
    different_index = _get_different_list_index(to_expand_headers, reference_headers)
    output_grouping = dict()
    for individual in to_expand_headers[different_index]:
        new_nested_headers = copy.deepcopy(reference_headers)
        new_nested_headers[different_index] = [individual]
        output_grouping[individual] = new_nested_headers
    return output_grouping

def _get_different_list_index(work_list, reference_list):
    for index, positional_list in enumerate(reference_list):
        if work_list[index] != positional_list:
            return index

balance_tolerance = 1E-2

def check_use_ressource(IOT, headers_grouping, use_headers, ressource_headers, tolerance=balance_tolerance):
    use_headers = _consolidate_headers(use_headers, headers_grouping, get_headers_from(IOT))
    ressource_headers = _consolidate_headers(ressource_headers, headers_grouping, get_headers_from(IOT))
    uses = _slice(IOT, use_headers).sum()
    ressources = _slice(IOT, ressource_headers).sum(axis=1)
    balances = uses - ressources < tolerance
    if not all(balances):
        sys.stderr.write("Warning : unbalanced IOT"+linebreaker)
        sys.stderr.write(', '.join([activities for activities, balanced in zip(use_headers[0], balances) if not balanced])+linebreaker)

def _consolidate_headers(headers_names, headers_grouping, reference_headers):
    expanded_headers = _map_aggregate_to_activities(headers_names, headers_grouping)
    expanded_merged_headers = functools.reduce(_merge_headers, expanded_headers)
    return list(map(lambda positional_header: _get_and_change_order_of(positional_header, reference_headers), expanded_merged_headers))

def _merge_headers(first_header, second_header):
    merged_headers = list()
    for first_positional_header, second_positional_header in zip(first_header, second_header):
        merged_headers.append(list(set(first_positional_header+second_positional_header)))
    return merged_headers