# coding : utf-8

import pandas as pd
import src.Loading_data_lib as ld
import src.Aggregation as Agg
from src.paths import (data_dir)
from typing import (Dict, List, Tuple)

Coordinates = Tuple[List[str], List[str]]


def get_IOT_values(study_dashb: Dict[str, str]
                   ) -> Dict[str, pd.DataFrame]:
    IOT_val = ld.read_table(study_dashb['studydata_dir'] / 'IOT_Val.csv',
                            delimiter=';')
    common_activities_mapping_path = study_dashb['studydata_dir'] / 'common_activities_mapping.csv'
    common_activities_mapping = ld.read_activities_mapping(common_activities_mapping_path,
                                                           delimiter=',',
                                                           headers=ld.get_headers_from(IOT_val))
    IOT_val, common_activities_mapping = Agg.apply_aggregation(study_dashb,
                                                               IOT_val,
                                                               common_activities_mapping)
    value_activities_mapping = ld.extend_activities_mapping(study_dashb['studydata_dir'] / 'value_activities_mapping.csv',
                                                            IOT_val,
                                                            common_activities_mapping)
    value_categories_coord = ld.read_categories_coordinates(study_dashb['studydata_dir'] / 'value_categories_coordinates.csv',
                                                            delimiter=',')
    value_coord = ld.map_categories_to_activities_coordinates(value_categories_coord,
                                                              value_activities_mapping)
    value_coord = ld.disaggregate_in_coordinates(value_coord,
                                                 ['FC', 'OthPart_IOT'], 'IC')

    value_ressource_categories = ['IC', 'OthPart_IOT']
    use_categories = ['IC', 'FC']
    ld.is_IOT_balanced(use_categories, value_ressource_categories,
                       IOT_val, value_coord)
    current_ERE = ld.get_ERE(use_categories, value_ressource_categories,
                             IOT_val, value_coord)
    value_ressources_to_correct = {'M_value': (IOT_val.loc[value_coord['M_value']] != 0,
                                               IOT_val.loc[value_coord['M_value']] - current_ERE),
                                   'Profit_margin': (IOT_val.loc[value_coord['M_value']] == 0,
                                                     IOT_val.loc[value_coord['Profit_margin']] - current_ERE)}
    for ressource_to_correct, correction_info in value_ressources_to_correct.items():
        correction_condition, correction_value = correction_info
        ld.modify_activity_value(IOT_val, value_coord[ressource_to_correct],
                                 correction_condition, correction_value)
    ld.is_IOT_balanced(use_categories, value_ressource_categories,
                       IOT_val, value_coord)
    return ld.extract_IOTs_from(IOT_val, value_coord), common_activities_mapping
