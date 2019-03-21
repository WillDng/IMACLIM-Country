# coding : utf-8

from typing import (Any, Dict, Iterable, List, Union)
from src.paths import study_dir
import src.common_utils as cu


def read_(study_ISO: str)-> Dict[str, str]:
    study_frame_path = 'study_frames_'+ study_ISO
    dashboard_filepath = 'Dashboard_' + study_ISO + '.csv'
    dashboard_path = study_dir / study_frame_path / dashboard_filepath
    dashboard_raw = cu._read_csv(dashboard_path, delimiter=';')
    dashboard_data = filter_comment_in_dashboard(dashboard_raw)
    filtered_dashboard, duplicates = cu.filter_list_duplicate(dashboard_data,
                                                              dashboard_path)
    cu.raise_if_duplicates(duplicates, dashboard_path)
    dashboard = nested_list_to_dict(filtered_dashboard)
    dashboard = interpret_boolean_in_dict(dashboard)
    dashboard['Country_selection'] = study_ISO
    return dashboard


def filter_comment_in_dashboard(dashboard_raw: Iterable[List[str]]
                                )-> Dict[str, str]:
    out_dashboard = list()
    for row in dashboard_raw:
        if not row[0].startswith('//'):
            out_dashboard.append(row)
    return iter(out_dashboard)


def compose_duplicates_message(dashb_categories_duplicates: List[str]) -> None:
    dashb_categories_mess = {'H_DISAGG':"various types of disaggregation profiles of households have been selected in Dashboard",
                             'AGG_type':"various types of aggregation profiles of sectors have been selected in Dashboard",
                             'System_Resol':"various types of resolution system have been selected in Dashboard",
                             'Resol_Mode':"various types of simulation mode have been selected in Dashboard",
                             'Scenario':"various types of scenario have been selected in Dashboard. The model isn't ready yet to run several Scenarios successively.",
                             'Macro_nb':"various types of macroeconomic framework been selected in Dashboard.",
                             'CO2_footprint':"You have to choose whether or not you want to realise an Input-Output Analysis about carbon footprint.",
                             'Output_files':"You have to choose whether or not you want to print outputs in external files."}
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


def interpret_boolean_in_dict(input_dict: Dict[str, str]
                              ) -> Dict[str, Union[str, bool]]:
    boolean_str_map = {'True':True,
                       'False':False}
    output_dict = dict()
    for key, value in input_dict.items():
        if value in boolean_str_map.keys():
            output_dict[key] = boolean_str_map[value]
        else:
            output_dict[key] = value
    return output_dict

