# coding : utf-8

import copy
import pandas as pd
import pathlib as pl
import src.common_utils as cu
import src.Loading_data_lib as ldl
from src.paths import data_dir
from typing import (Dict, Iterator, List, Union)
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


def aggregate_IOT(IOT: pd.DataFrame,
                  aggregation: Dict[str, List[str]]
                  ) -> pd.DataFrame:
    index_aggregation  = complete_missing_keys(aggregation, IOT.index)
    index_aggregated_IOT = IOT.groupby(index_aggregation, sort=False).sum()
    columns_aggregation = complete_missing_keys(aggregation, IOT.columns)
    aggregated_IOT = index_aggregated_IOT.groupby(columns_aggregation, axis=1, sort=False).sum()
    return aggregated_IOT


def complete_missing_keys(dict_to_complete, headers):
    completed_dict = copy.deepcopy(dict_to_complete)
    missing_keys = set(headers) - set(dict_to_complete.keys())
    for missing_key in missing_keys:
        completed_dict[missing_key] = missing_key
    return completed_dict


def aggregate_activities_mapping(activities_mapping: Dict[str, List[str]],
                                 aggregation_mapping: Dict[str, List[str]],
                                 headers: List[pd.Index]
                                 ) -> Dict[str, List[str]]:
    aggregated_activities_mapping = dict()
    return aggregated_activities_mapping


def sort_remaining_activities(remaining_activities: Set[str],
                              unordered_agg_activities: List[str],
                              categoryless_activities: List[str],
                              ordering_header: pd.Index
                              ) -> (List[str], List[str]):
    if remaining_activities.issubset(set(ordering_header)):
        unordered_agg_activities += list(remaining_activities)
    else:
        categoryless_activities.extend(list(remaining_activities))
    return unordered_agg_activities, categoryless_activities


def treat_remaining(grouping_name: str,
                    remaining_activities: List[str],
                    values_aggregation: Dict[str, List[str]],
                    aggregated_mappping: Dict[str, Dict[str, List[str]]],
                    header: pd.Index) -> Dict[str, Dict[str, List[str]]]:
    treat_function = has_remaining_treatment[grouping_name]
    new_aggregated_mapping = treat_function(remaining_activities,
                                            values_aggregation,
                                            aggregated_mappping,
                                            header)
    return new_aggregated_mapping


def hybrid_treatment(remaining_activities: List[str],
                     values_aggregation: Dict[str, List[str]],
                     aggregated_mappping: Dict[str, Dict[str, List[str]]],
                     header: pd.Index) -> Dict[str, Dict[str, List[str]]]:
    unordered_agg_activities, remaining_activities = aggregate_in_list(remaining_activities,
                                                                       values_aggregation)
    remaining_header = 'NonHybridCommod'
    unordered_agg_activities.extend(aggregated_mappping[remaining_header])
    aggregated_mappping[remaining_header] = ldl.change_order_of(unordered_agg_activities,
                                                                header)
    return aggregated_mappping

has_remaining_treatment = {'Hybrid': hybrid_treatment}




def aggregate_in_list(list_to_aggregate: List[str],
                      aggregation_mapping: Dict[str, List[str]]
                      ) -> (List[str], Set[str]):
    aggregated_list = list()
    remaining_items = set(list_to_aggregate)
    for group, members in aggregation_mapping.items():
        members_set = set(members)
        if members_set.issubset(remaining_items):
            aggregated_list.append(group)
            remaining_items -= members_set
    return list(aggregated_list), remaining_items
