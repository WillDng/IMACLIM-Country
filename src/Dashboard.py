# coding : utf-8

from typing import (Any, Dict, Iterator, List, Union)
from src.paths import study_frames_dir
import src.common_utils as cu
from src.common_utils import InputError
import copy

def read_(study_ISO: str)-> Dict[str, str]:
    dashboard_path = study_frames_dir / study_ISO / 'Dashboard.csv'
    dashboard_raw = cu._read_csv(dashboard_path, delimiter=';')
    dashboard_data = filter_comment_in_dashboard(dashboard_raw)
    dashboard_data = _convert_dashboard_values(dashboard_data)
    _validate_or_raise_dashboard(copy.deepcopy(dashboard_data))
    dashboard = nested_list_to_dict(dashboard_data)
    dashboard = convert_boolean_in_dict(dashboard)
    dashboard['Country'] = study_ISO
    return dashboard


def filter_comment_in_dashboard(dashboard_raw: Iterator[List[str]]
                                )-> Dict[str, str]:
    out_dashboard = list()
    for row in dashboard_raw:
        if not row[0].startswith('//'):
            out_dashboard.append(row)
    return iter(out_dashboard)


boolean_str_map = {'True':True,
                   'False':False}


def _convert_dashboard_values(dashboard_data: Iterator[List[List[str]]]
                             ) -> Iterator[List[List[Union[str, int, bool]]]]:
    out_dashboard_data = list()
    for row in dashboard_data:
        try:
            value = row[1]
        except IndexError:
            value = None
        if is_bool(value):
            row[1] = boolean_str_map[value]
        elif is_int(value):
            row[1] = int(value)
        out_dashboard_data.append(row)
    return iter(out_dashboard_data)


def is_bool(entry: str) -> bool:
    if entry in boolean_str_map.keys():
        return True
    return False


def is_int(entry: str) -> bool:
    try:
        int(entry)
        return True
    except (ValueError, TypeError):
        return False


def _validate_or_raise_dashboard(dashboard_data: Iterator[List[List[Union[str, int, bool]]]]
                                 ) -> None:
    data_to_validate = list(dashboard_data)
    iteration_message = _compose_iteration_nb_message(data_to_validate)
    _, duplicates = cu.filter_list_duplicate(data_to_validate)
    duplicates_message = _compose_duplicates_message(duplicates)
    if iteration_message or duplicates_message:
        raise InputError(iteration_message+'\n'+duplicates_message)

def _compose_iteration_nb_message(dashb_data: List[List[Union[str, int, bool]]]
                                  ) -> Union[str, None]:
    for row in dashb_data:
        if ((row[0] == 'Nb_Iter') and (row[1] < 0 )):
            return 'the number of iteration should be positive'
    return ''

def _compose_duplicates_message(dashb_categories_duplicates: List[str]) -> None:
    dashb_categories_mess = {'H_DISAGG':"various types of disaggregation profiles of households have been selected in Dashboard",
                             'AGG_type':"various types of aggregation profiles of sectors have been selected in Dashboard",
                             'System_Resol':"various types of resolution system have been selected in Dashboard",
                             'Resol_Mode':"various types of simulation mode have been selected in Dashboard",
                             'Scenario':"various types of scenario have been selected in Dashboard. The model isn't ready yet to run several Scenarios successively.",
                             'Macro_nb':"various types of macroeconomic framework been selected in Dashboard.",
                             'CO2_footprint':"You have to choose whether or not you want to realise an Input-Output Analysis about carbon footprint.",
                             'Output_files':"You have to choose whether or not you want to print outputs in external files."}
    if not dashb_categories_duplicates:
        return ''
    messages = list()
    for duplicate_dashb_category in dashb_categories_duplicates:
        messages.append(dashb_categories_mess[duplicate_dashb_category])
    return '\n'.join(messages)


def nested_list_to_dict(nested_list: List[List[str]],
                        key_col: int=0,
                        value_col: int=None) -> Dict[str, str]:
    output_dict = dict()
    for row in nested_list:
        key = row[key_col]
        if value_col:
            value = row[value_col]
        else:
            value = row
        value.remove(key)
        output_dict[key] = value_if_alone(value)
    return output_dict


def value_if_alone(input_list: List[Any])-> List[Any]:
    if len(input_list) == 0:
        return None
    elif len(input_list) == 1:
        return input_list[0]
    else:
        return iter(input_list)


def convert_boolean_in_dict(input_dict: Dict[str, str]
                              ) -> Dict[str, Union[str, bool]]:
    output_dict = dict()
    for key, value in input_dict.items():
        if value in boolean_str_map.keys():
            output_dict[key] = boolean_str_map[value]
        else:
            output_dict[key] = value
    return output_dict

