# coding : utf-8

import sys
import os
import csv
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

def read_IOT_aggregation_from(IOT_aggregation_path, delimiter='|'):
    """ Hypothesis : in first column are the names of the individuals and in columns aggregates names """
    reader = _get_reader_from(IOT_aggregation_path, delimiter)
    IOT_aggregation = dict()
    for individual_description in reader:
        individual = individual_description[0]
        aggregates = individual_description[1:]
        if not aggregates:
            sys.stderr.write("Warning : delimiter might not be correctly informed in function")
            return            
        for aggregate in aggregates:
            if aggregate not in IOT_aggregation:
                IOT_aggregation[aggregate] = list()
            if individual not in IOT_aggregation[aggregate]:
                IOT_aggregation[aggregate].append(individual)
            else:
                pass
                #FIXME should raise warning ?
    for aggregate, individuals in IOT_aggregation.items():
        IOT_aggregation[aggregate] = tuple(individuals)
    return IOT_aggregation

def _get_reader_from(path, delimiter):
    return csv.reader(open(path), delimiter=delimiter)

def slice_(IOT, field_headers):
    sliced_IOT = IOT.loc[field_headers]
    if sliced_IOT.isnull().values.any():
        sys.stderr.write("Warning : IOT headers might be ill informed"+linebreaker)
    return sliced_IOT

def read_grouping_from(path, delimiter='|'):
    reader = _get_reader_from(path, delimiter)
    grouping = dict()
    for row in reader:
        group = row[0]
        if group not in grouping:
            grouping[group] = list()
        grouping[group] = row[1:]
    return grouping