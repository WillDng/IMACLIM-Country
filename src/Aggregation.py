# coding : utf-8

import pathlib as pl
import src.common_utils as cu
import src.Loading_data_lib as ldl
from src.paths import data_dir
import collections
from typing import (Dict, Iterator, List, Union)
import copy
import ipdb

# def read_file(data_path: pl.Path) -> Dict[str, Dict[str, str]]:
#      iter
#     iter_data = _read_csv(path, delimiter)

def read_aggregation(dashb: Dict[str, str]):
    agg_filepath = dashb['data_dir'] / 'aggregation.csv'
    aggregation_raw_data = cu._read_csv(agg_filepath, delimiter=';')
    #FIXME delimiter is hardcoded
    agg_header, aggregation_raw_data = list(filter(None, aggregation_raw_data.__next__())), list(aggregation_raw_data)
    chosen_aggregation = dashb['AGG_type']
    if chosen_aggregation not in agg_header:
        raise KeyError('Chosen aggregation is not available at ' + agg_filepath)
    agg_index = agg_header.index(chosen_aggregation)+1
    agg_keys = cu.fill_dict(aggregation_raw_data, agg_index)
    agg_values = ldl.extract_activities_mapping(aggregation_raw_data,
                                                agg_filepath,
                                                col=agg_index)
    return agg_keys, agg_values


def complete_missing_keys(dict_to_commplete, headers):
    completed_dict = copy.deepcopy(dict_to_commplete)
    missing_keys = set(headers) - set(dict_to_commplete.keys())
    for missing_key in missing_keys:
        completed_dict[missing_key] = missing_key
    return completed_dict
