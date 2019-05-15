# coding : utf-8

import copy
import pandas as pd
import pathlib as pl
import src.common_utils as cu
import src.Loading_data_lib as ldl
from typing import (Dict, List, Set, Tuple, Union)


def read_aggregation(study_dashb: Dict[str, str]
                     ) -> (Dict[str, str], Dict[str, List[str]]):
    chosen_aggregation = study_dashb.get('AGG_type', None)
    if chosen_aggregation is None:
        return None, None
    agg_filepath = study_dashb['studydata_dir'] / 'aggregation.csv'
    # FIXME delimiter is hardcoded
    aggregation_raw_data = cu._read_csv(agg_filepath, delimiter=';')
    agg_header, aggregation_raw_data = list(filter(None, aggregation_raw_data.__next__())), list(aggregation_raw_data)
    return get_aggregation_items(chosen_aggregation,
                                 agg_header,
                                 agg_filepath,
                                 aggregation_raw_data)


def get_aggregation_items(chosen_aggregation: str,
                          aggregation_header: List[str],
                          aggregation_filepath: pl.Path,
                          aggregation_raw_data: List[List[str]]
                          ) -> Union[Tuple[Dict[str, str], Dict[str, List[str]]],
                                     Tuple[None, None]]:
    if chosen_aggregation not in aggregation_header:
        raise KeyError('Chosen aggregation is not available at ' + str(aggregation_filepath))
    agg_index = aggregation_header.index(chosen_aggregation) + 1
    agg_keys = cu.fill_dict(aggregation_raw_data, agg_index)
    agg_values = cu.extract_aggregation_mapping(aggregation_raw_data,
                                                col=agg_index)
    return agg_keys, agg_values


def aggregate_IOT(IOT: pd.DataFrame,
                  aggregation: Dict[str, List[str]]
                  ) -> pd.DataFrame:
    index_aggregation = complete_missing_keys(aggregation, IOT.index)
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


def aggregate_activities_mapping(activities_mapping: Dict[str, Dict[str, List[str]]],
                                 values_aggregation: Dict[str, List[str]],
                                 headers: List[pd.DataFrame],
                                 ) -> Dict[str, Dict[str, List[str]]]:
    aggregated_activities_mapping = dict()
    for grouping_name, grouping_values in activities_mapping.items():
        aggregated_mappping = dict()
        categoryless_activities = list()
        for category, activities in grouping_values.items():
            unordered_agg_activities, remaining_activities = aggregate_in_list(activities,
                                                                               values_aggregation)
            ordering_header = ldl.get_matching_header_for(activities,
                                                          headers)
            if remaining_activities:
                unordered_agg_activities, categoryless_activities = sort_remaining_activities(remaining_activities,
                                                                                              unordered_agg_activities,
                                                                                              categoryless_activities,
                                                                                              ordering_header)
            aggregated_mappping[category] = ldl.change_order_of(unordered_agg_activities,
                                                                ordering_header)
        if categoryless_activities and (has_remaining_treatment.get(grouping_name, False)):
            aggregated_mappping = treat_remaining(grouping_name,
                                                  categoryless_activities,
                                                  values_aggregation,
                                                  aggregated_mappping,
                                                  ordering_header)
        aggregated_activities_mapping[grouping_name] = aggregated_mappping
    return cu.unpack_nested_dict(aggregated_activities_mapping)


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


def is_aggregation(aggregation_items: (Dict[str, str],
                                       Dict[str, List[str]])):
    if aggregation_items[0] is not None:
        return True
    return False


def add_SpeMarg(aggregation_items: Tuple[Dict[str, str],
                                         Dict[str, List[str]]]
                ) -> Tuple[Dict[str, str],
                           Dict[str, List[str]]]:
    keys_aggregation, values_aggregation = aggregation_items
    return (add_spemarg_mapping(keys_aggregation),
            add_spemarg_mapping(values_aggregation))


def add_spemarg_mapping(input_mapping: Dict[str, Union[str, List[str]]]
                        ) -> Dict[str, Union[str, List[str]]]:
    out_mapping = dict()
    for key, value in input_mapping.items():
        if isinstance(value, list):
            modified_value = list(map(get_spemarg, value))
        else:
            modified_value = get_spemarg(value)
        out_mapping[get_spemarg(key)] = modified_value
    out_mapping.update(input_mapping)
    return out_mapping


def aggregate_IOT_and_activities_mapping(entry_IOT: pd.DataFrame,
                                         aggregation_items: Tuple[Dict[str, str],
                                                                  Dict[str, List[str]]],
                                         # keys_aggregation: Dict[str, List[str]],
                                         common_activities_mapping: Dict[str, Dict[str, List[str]]]
                                         ) -> (pd.DataFrame, Dict[str, List[str]]):
    keys_aggregation, values_aggregation = aggregation_items
    aggregated_IOT = aggregate_IOT(entry_IOT,
                                   keys_aggregation)
    common_activities_mapping = aggregate_activities_mapping(common_activities_mapping,
                                                             values_aggregation,
                                                             ldl.get_headers_from(aggregated_IOT))
    return aggregated_IOT, common_activities_mapping


spemarg_prefix = 'SpeMarg_'


def get_spemarg(input_string: str) -> str:
    return spemarg_prefix + input_string
