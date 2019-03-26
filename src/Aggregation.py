# coding : utf-8

import pathlib as pl
import src.common_utils as cu
from src.paths import data_dir
import collections
from typing import (Dict, Iterator, List)
import copy
import ipdb

# def read_file(data_path: pl.Path) -> Dict[str, Dict[str, str]]:
#      iter
#     iter_data = _read_csv(path, delimiter)

def extract_agg(raw_data: Iterator) -> Dict[str, Dict[str, str]]:
    out_agg = dict()
    agg_types = list(filter(None, raw_data.__next__()))
    for agg_type in agg_types:
        out_agg[agg_type] = dict()
def extract_agg(raw_data: Iterator, agg_types: List[str]
                ) -> Dict[str, Dict[str, str]]:
    out_agg = collections.defaultdict(dict)
    for activity_row in raw_data:
        for agg_type_index, agg_type in enumerate(agg_types):
            out_agg[agg_type][activity_row[0]] = activity_row[agg_type_index+1]
    return dict(out_agg)


def complete_missing_keys(dict_to_commplete, headers):
    completed_dict = copy.deepcopy(dict_to_commplete)
    missing_keys = set(headers) - set(dict_to_commplete.keys())
    for missing_key in missing_keys:
        completed_dict[missing_key] = missing_key
    return completed_dict