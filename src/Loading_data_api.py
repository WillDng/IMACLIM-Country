# coding : utf-8

import pandas as pd
from src import (common_utils as cu,
                 Aggregation as Agg,
                 Loading_data_lib as ld)
from typing import (Dict, List, Tuple, Union)
import ipdb

Coordinates = Tuple[List[str], List[str]]


use_categories = ['IC', 'FC']


def get_IOT_values(study_dashb: Dict[str, str]
                   ) -> (Dict[str, pd.DataFrame],
                         Dict[str, List[str]],
                         Union[Dict[str, str], None]):
    IOT_val = ld.read_table(study_dashb['studydata_dir'] / 'IOT_Val.csv',
                            delimiter=';')
    common_activities_mapping = ld.read_activities_mapping(study_dashb['studydata_dir'] / 'common_activities_mapping.csv',
                                                           delimiter=',',
                                                           headers=ld.get_headers_from(IOT_val))
    IOT_val, common_activities_mapping, keys_aggregation = Agg.apply_value_aggregation(study_dashb,
                                                                                       IOT_val,
                                                                                       common_activities_mapping)
    value_activities_mapping = ld.extend_activities_mapping(study_dashb['studydata_dir'] / 'value_activities_mapping.csv',
                                                            IOT_val,
                                                            common_activities_mapping)
    value_coord = ld.get_categories_coordinates(study_dashb['studydata_dir'] / 'value_categories_coordinates.csv',
                                                value_activities_mapping)
    value_coord = ld.disaggregate_in_coordinates(value_coord,
                                                 ['FC', 'OthPart_IOT'], 'IC')
    value_ressource_categories = ['IC', 'OthPart_IOT']
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
    return ld.extract_IOTs_from(IOT_val, value_coord), common_activities_mapping, keys_aggregation


def get_IOT_quantities(study_dashb: Dict[str, str],
                       common_activities_mapping: Dict[str, List[str]],
                       keys_aggregation: Union[Dict[str, str], None]
                       ) -> Dict[str, pd.DataFrame]:
    IOT_quantity = ld.read_table(study_dashb['studydata_dir'] / 'IOT_Qtities.csv',
                                 delimiter=';',
                                 skipfooter=1,
                                 engine='python')
    if keys_aggregation:
        IOT_quantity = Agg.aggregate_IOT(IOT_quantity, keys_aggregation)
    quantity_activities_mapping = ld.extend_activities_mapping(study_dashb['studydata_dir'] / 'quantity_activities_mapping.csv',
                                                               IOT_quantity,
                                                               common_activities_mapping)
    quantity_coord = ld.get_categories_coordinates(study_dashb['studydata_dir'] / 'quantity_categories_coordinates.csv',
                                                   quantity_activities_mapping)
    quantity_coord = ld.disaggregate_in_coordinates(quantity_coord,
                                                    ['FC'], 'IC')
    quantity_ressource_categories = ['M', 'Y']
    ld.is_IOT_balanced(use_categories, quantity_ressource_categories,
                       IOT_quantity, quantity_coord)
    current_ERE = ld.get_ERE(use_categories, quantity_ressource_categories,
                             IOT_quantity, quantity_coord)
    quantity_uses_to_correct = {'Y': (IOT_quantity.loc[quantity_coord['Y']] != 0,
                                      IOT_quantity.loc[quantity_coord['Y']] + current_ERE),
                                'X': (IOT_quantity.loc[quantity_coord['Y']] == 0,
                                      IOT_quantity.loc[quantity_coord['X']] - current_ERE)}
    for use_to_correct, correction_info in quantity_uses_to_correct.items():
        correction_condition, correction_value = correction_info
        ld.modify_activity_value(IOT_quantity, quantity_coord[use_to_correct],
                                 correction_condition, correction_value)
    ld.is_IOT_balanced(use_categories, quantity_ressource_categories,
                       IOT_quantity, quantity_coord)

    return ld.extract_IOTs_from(IOT_quantity, quantity_coord), quantity_coord


def get_IOT_prices(study_dashb: Dict[str, str],
                   keys_aggregation: Union[Dict[str, str], None],
                   quantity_coord: Dict[str, Tuple[List[str], List[str]]]
                   ) -> Dict[str, pd.DataFrame]:
    IOT_prices = ld.read_table(study_dashb['studydata_dir'] / 'IOT_Prices.csv',
                               delimiter=';',
                               skipfooter=1,
                               engine='python')
    if keys_aggregation:
        IOT_prices = Agg.aggregate_IOT(IOT_prices,
                                       keys_aggregation)
    return ld.extract_IOTs_from(IOT_prices, quantity_coord)


def get_IOT_CO2(study_dashb: Dict[str, str],
                common_activities_mapping: Dict[str, List[str]],
                keys_aggregation: Union[Dict[str, str], None],
                ) -> Dict[str, pd.DataFrame]:
    IOT_CO2 = ld.read_table(study_dashb['studydata_dir'] / 'IOT_CO2.csv',
                            delimiter=';',
                            skipfooter=1,
                            engine='python')
    if keys_aggregation:
        IOT_CO2 = Agg.aggregate_IOT(IOT_CO2,
                                    keys_aggregation)
    CO2_activities_mapping = ld.extend_activities_mapping(study_dashb['studydata_dir'] / 'CO2_activities_mapping.csv',
                                                          IOT_CO2,
                                                          common_activities_mapping)
    CO2_activities_coord = ld.get_categories_coordinates(study_dashb['studydata_dir'] / 'CO2_categories_coordinates.csv',
                                                         CO2_activities_mapping)
    return ld.extract_IOTs_from(IOT_CO2, CO2_activities_coord)


def get_account_table(study_dashb: Dict[str, str]
                      ) -> Dict[str, Union[pd.Series, float]]:
    account_table = ld.read_table(study_dashb['studydata_dir'] / 'DataAccountTable.csv',
                                  delimiter=';',
                                  skipfooter=1,
                                  engine='python')
    selected_accounts = cu.read_dict(study_dashb['studydata_dir'] / study_dashb['DataAccount_params'],
                                     value_col=1,
                                     delimiter=';')
    return ld.extract_accounts(account_table, selected_accounts)


def get_labour(study_dashb: Dict[str, str]
               ) -> pd.Series:
    return ld.read_table(study_dashb['studydata_dir'] / 'Labour.csv',
                         delimiter=';',
                         skipfooter=1,
                         engine='python')


def get_demography(study_dashb: Dict[str, str]
                   ) -> Dict[str, float]:
    demography_table = ld.read_table(study_dashb['studydata_dir'] / 'Demography.csv',
                                     delimiter=';',
                                     skipfooter=1,
                                     engine='python')
    to_extract_demography = {line: demography_table.columns[0] for line in demography_table.index}
    return ld.pick_selection(demography_table,
                             to_extract_demography)
