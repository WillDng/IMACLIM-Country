# coding : utf-8

import os
import sys
import collections
import copy
import csv
import numpy as np
import pandas

linebreaker = '\n'
dir_separator = os.sep

def import_IOT(IOT_file_path, **kwargs):
    read_IOT = pandas.read_csv(IOT_file_path, 
                               index_col=0,
                               **kwargs)
    if len(get_IOT_header_from(read_IOT)) < 2:
        IOT_name = get_filename_from(IOT_file_path)
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in "+IOT_name+linebreaker)
    return read_IOT

def get_IOT_header_from(IOT):
    return IOT.columns.tolist()

def get_filename_from(path):
    return path.split(dir_separator)[-1]

def read_IOT_aggregation_from(IOT_aggregation_path, delimiter='|', headers=None):
    """ Hypothesis : in first column are the names of the individuals and in columns aggregates names """
    reader = _get_reader_from(IOT_aggregation_path, delimiter)
    IOT_aggregation = collections.defaultdict(list)
    for individual_description in reader:
        individual = individual_description[0]
        aggregates = individual_description[1:]
        if not aggregates:
            sys.stderr.write("Warning : delimiter might not be correctly informed in function")
            return            
        for aggregate in aggregates:
            if individual not in IOT_aggregation[aggregate]:
                IOT_aggregation[aggregate].append(individual)
            else:
                pass
                #FIXME should raise warning ?
    if headers:
        _change_individuals_order_in(IOT_aggregation, headers)
    return IOT_aggregation

def _get_reader_from(path, delimiter):
    return csv.reader(open(path), delimiter=delimiter)

def _change_individuals_order_in(aggregation, reference_headers):
    for aggregate, individuals in aggregation.items():
        reference_header = _get_correct_header(individuals, reference_headers)
        aggregation[aggregate] = _change_order_of(individuals, reference_header)

def return_original_type(function):
    def wrapper_original_type(reference_object, other_object):
        reference_type = type(reference_object)
        function_result = function(reference_object, other_object)
        return reference_type(function_result)
    return wrapper_original_type

@return_original_type
def _get_correct_header(reference_array, headers):
    chose_array = max(headers, key=lambda header: len(np.intersect1d(reference_array, header)))
    return chose_array

@return_original_type
def _change_order_of(iterable, reference_array):
    reordered_array = np.intersect1d(reference_array, np.array(iterable))
    return reordered_array

def read_grouping_from(path, delimiter='|'):
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
        out_IOT[var_name] = _slice_(IOT, field_header)
    return out_IOT

def translate_grouping_to_individuals(grouping, aggregation):
    for group_name, groups in grouping.items():
        grouping[group_name] = list(map(lambda aggregate:aggregation[aggregate], groups))

def _slice_(IOT, field_headers):
    sliced_IOT = IOT.loc[tuple(field_headers)]
    if sliced_IOT.isnull().values.any():
        sys.stderr.write("Warning : IOT headers might be ill informed"+linebreaker)
    return sliced_IOT

to_expand_variables = ['FC', 'OthPart_IOT']
reference_variable = 'IC'

def add_individuals_in_expanded_grouping(expanded_grouping):
    for to_expand_variable in to_expand_variables:
        new_grouping = _generate_individuals_in_expanded_grouping(expanded_grouping[to_expand_variable], expanded_grouping[reference_variable])
        expanded_grouping.update(new_grouping)

def _generate_individuals_in_expanded_grouping(to_expand_headers, reference_headers):
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