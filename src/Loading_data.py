# coding : utf-8

import numpy as np
import pandas as pd
from typing import (Dict, List, Tuple, Union)
from src import (Aggregation as Agg,
                 common_utils as cu,
                 Households_disag as hhd,
                 Loading_data_lib as ldl)
from src.parameters import file_delimiter
import ipdb


Coordinates = Tuple[List[str], List[str]]


use_categories = ['IC', 'FC']
FC_to_disaggregate = 'C'
account_to_disaggregate = 'Households'


def load_data(study_dashb: Dict[str, str]
              ) -> Dict[str, pd.DataFrame]:
    (aggregation_items, IOT_val_disagg,
     common_activities_mapping, disaggregation_rate) = read_and_check_input_files(study_dashb)
    Initial_quantitites, quantity_coord = get_IOT_quantities(study_dashb,
                                                             common_activities_mapping,
                                                             aggregation_items,
                                                             disaggregation_rate)
    Initial_prices = get_IOT_prices(study_dashb,
                                    quantity_coord,
                                    disaggregation_rate)
    Initial_DataAccount = get_account_table(study_dashb,
                                            disaggregation_rate)
    (Initial_values, value_coord, IOT_val) = get_IOT_values(study_dashb,
                                                            IOT_val_disagg,
                                                            common_activities_mapping,
                                                            aggregation_items)

    Initial_CO2 = get_IOT_CO2(study_dashb,
                              common_activities_mapping,
                              aggregation_items)
    Initial_labour = get_labour(study_dashb,
                                aggregation_items)
    Initial_demography = get_demography(study_dashb)
    Initial_import_values = get_import_rates(study_dashb,
                                             IOT_val_disagg,
                                             aggregation_items,
                                             value_coord)
    Initial_CO2_tax = get_CO2_tax(quantity_coord)


def read_and_check_input_files(study_dashb: Dict[str, str]):
    aggregation_items = Agg.read_aggregation(study_dashb)
    IOT_val_disagg = cu.read_table(study_dashb['studydata_dir'] / 'IOT_Val.csv',
                                   delimiter=file_delimiter)
    common_activities_mapping = get_common_activies_mapping(study_dashb,
                                                            IOT_val_disagg)
    disaggregation_rate = hhd.read_disaggregation_rate(study_dashb)
    return (aggregation_items, IOT_val_disagg,
            common_activities_mapping, disaggregation_rate)


def get_common_activies_mapping(study_dashb: Dict[str, str],
                                IOT_values: pd.DataFrame
                                ) -> Dict[str, Dict[str, List[str]]]:
    common_activities_mapping = ldl.read_activities_mapping(study_dashb['studydata_dir'] / 'common_activities_mapping.csv',
                                                            delimiter=',')
    common_activities_mapping = ldl.change_activities_mapping_order(common_activities_mapping,
                                                                    ldl.get_headers_from(IOT_values))
    return common_activities_mapping


def get_IOT_quantities(study_dashb: Dict[str, str],
                       common_activities_mapping: Dict[str, List[str]],
                       aggregation_items: (Dict[str, List[str]],
                                           Dict[str, str]),
                       disaggregation_rate: pd.Index
                       ) -> (Dict[str, pd.DataFrame],
                             List[str], List[str]):
    IOT_quantity = cu.read_table(study_dashb['studydata_dir'] / 'IOT_Qtities.csv',
                                 delimiter=file_delimiter,
                                 skipfooter=1,
                                 engine='python')
    if Agg.is_aggregation(aggregation_items):
        IOT_quantity, common_activities_mapping = Agg.aggregate_IOT_and_activities_mapping(IOT_quantity,
                                                                                           aggregation_items,
                                                                                           common_activities_mapping)
    quantity_activities_mapping = ldl.extend_activities_mapping(study_dashb['studydata_dir'] / 'quantity_activities_mapping.csv',
                                                                IOT_quantity,
                                                                common_activities_mapping)
    if disaggregation_rate is not None:
        IOT_quantity = hhd.disaggregate_IOT(FC_to_disaggregate,
                                            IOT_quantity,
                                            disaggregation_rate)
        quantity_activities_mapping = hhd.replace_disaggregated_in_(quantity_activities_mapping,
                                                                    FC_to_disaggregate,
                                                                    ldl.get_header_from(disaggregation_rate))
    quantity_coord = ldl.get_categories_coordinates(study_dashb['studydata_dir'] / 'quantity_categories_coordinates.csv',
                                                    quantity_activities_mapping)
    quantity_coord = ldl.disaggregate_in_coordinates(quantity_coord,
                                                     ['FC'], 'IC')
    quantity_ressource_categories = ['M', 'Y']
    ldl.is_IOT_balanced(use_categories, quantity_ressource_categories,
                        IOT_quantity, quantity_coord)
    current_ERE = ldl.get_ERE(use_categories, quantity_ressource_categories,
                              IOT_quantity, quantity_coord)
    quantity_uses_to_correct = {'Y': (IOT_quantity.loc[quantity_coord['Y']] != 0,
                                      IOT_quantity.loc[quantity_coord['Y']] + current_ERE),
                                'X': (IOT_quantity.loc[quantity_coord['Y']] == 0,
                                      IOT_quantity.loc[quantity_coord['X']] - current_ERE)}
    for use_to_correct, correction_info in quantity_uses_to_correct.items():
        correction_condition, correction_value = correction_info
        ldl.modify_activity_value(IOT_quantity, quantity_coord[use_to_correct],
                                  correction_condition, correction_value)
    ldl.is_IOT_balanced(use_categories, quantity_ressource_categories,
                        IOT_quantity, quantity_coord)

    return (ldl.extract_IOTs_from(IOT_quantity,
                                  quantity_coord),
            quantity_coord)


def get_IOT_prices(study_dashb: Dict[str, str],
                   quantity_coord: Dict[str, Tuple[List[str], List[str]]],
                   disaggregation_rate: pd.Index
                   ) -> Dict[str, pd.DataFrame]:
    IOT_prices = cu.read_table(study_dashb['studydata_dir'] / 'IOT_Prices.csv',
                               delimiter=file_delimiter,
                               skipfooter=1,
                               engine='python')
    # FIXME doesn't work when is aggregated
    # if keys_aggregation:
    #     IOT_prices = Agg.aggregate_IOT(IOT_prices,
    #                                    keys_aggregation)
    if disaggregation_rate is not None:
        IOT_prices = hhd.disaggregate_IOT_prices(FC_to_disaggregate,
                                                 IOT_prices,
                                                 disaggregation_rate)
    return ldl.extract_IOTs_from(IOT_prices,
                                 quantity_coord)


def get_account_table(study_dashb: Dict[str, str],
                      disaggregation_rate: pd.DataFrame
                      ) -> Dict[str, Union[pd.Series, float]]:
    account_table = cu.read_table(study_dashb['studydata_dir'] / 'DataAccountTable.csv',
                                  delimiter=file_delimiter,
                                  skipfooter=1,
                                  engine='python')
    selected_accounts = cu.read_dict(study_dashb['studydata_dir'] / study_dashb['DataAccount_params'],
                                     value_col=1,
                                     delimiter=file_delimiter)
    if disaggregation_rate is not None:
        account_table_disagregation_dir = study_dashb['disaggregation_rate_dir'] / 'DataAccountTable'
        disagg_level_account_table_rate = 'DataAccount_rate_' + study_dashb['H_DISAGG'] + '.csv'
        account_table_rate = cu.read_table(account_table_disagregation_dir / disagg_level_account_table_rate,
                                           delimiter=file_delimiter)
        account_table_mapping = cu.read_aggregation_mapping(account_table_disagregation_dir / 'Index_EconData.csv')
        hhd.modify_account_table_mapping(account_table_mapping,
                                         ldl.get_header_from(disaggregation_rate))
        account_table = hhd.disaggregate_account_table(account_to_disaggregate,
                                                       account_table,
                                                       account_table_rate,
                                                       account_table_mapping)
        selected_accounts = hhd.replace_disaggregated_in_(selected_accounts,
                                                          account_to_disaggregate,
                                                          ldl.get_header_from(disaggregation_rate))
    return ldl.extract_accounts(account_table,
                                selected_accounts)


def get_IOT_values(study_dashb: Dict[str, str],
                   IOT_val_disagg: pd.DataFrame,
                   common_activities_mapping: Dict[str, List[str]],
                   aggregation_items: (Dict[str, str],
                                       Dict[str, List[str]])
                   ) -> (Dict[str, pd.DataFrame],
                         Dict[str, List[str]],
                         Dict[str, Coordinates],
                         pd.DataFrame):
    IOT_val = IOT_val_disagg.copy()
    if Agg.is_aggregation(aggregation_items):
        IOT_val, common_activities_mapping = Agg.aggregate_IOT_and_activities_mapping(IOT_val,
                                                                                      aggregation_items,
                                                                                      common_activities_mapping)
    value_activities_mapping = ldl.extend_activities_mapping(study_dashb['studydata_dir'] / 'value_activities_mapping.csv',
                                                             IOT_val,
                                                             common_activities_mapping)
    value_coord = ldl.get_categories_coordinates(study_dashb['studydata_dir'] / 'value_categories_coordinates.csv',
                                                 value_activities_mapping)
    value_coord = ldl.disaggregate_in_coordinates(value_coord,
                                                  ['FC', 'OthPart_IOT'], 'IC')
    value_ressource_categories = ['IC', 'OthPart_IOT']
    ldl.is_IOT_balanced(use_categories, value_ressource_categories,
                        IOT_val, value_coord)
    current_ERE = ldl.get_ERE(use_categories, value_ressource_categories,
                              IOT_val, value_coord)
    value_ressources_to_correct = {'M_value': (IOT_val.loc[value_coord['M_value']] != 0,
                                               IOT_val.loc[value_coord['M_value']] - current_ERE),
                                   'Profit_margin': (IOT_val.loc[value_coord['M_value']] == 0,
                                                     IOT_val.loc[value_coord['Profit_margin']] - current_ERE)}
    for ressource_to_correct, correction_info in value_ressources_to_correct.items():
        correction_condition, correction_value = correction_info
        ldl.modify_activity_value(IOT_val, value_coord[ressource_to_correct],
                                  correction_condition, correction_value)
    ldl.is_IOT_balanced(use_categories, value_ressource_categories,
                        IOT_val, value_coord)
    return (ldl.extract_IOTs_from(IOT_val, value_coord),
            value_coord, IOT_val_disagg)


def get_IOT_CO2(study_dashb: Dict[str, str],
                common_activities_mapping: Dict[str, List[str]],
                aggregation_items: (Dict[str, List[str]],
                                    Dict[str, str])
                ) -> Dict[str, pd.DataFrame]:
    IOT_CO2 = cu.read_table(study_dashb['studydata_dir'] / 'IOT_CO2.csv',
                            delimiter=file_delimiter,
                            skipfooter=1,
                            engine='python')
    if Agg.is_aggregation(aggregation_items):
        IOT_CO2, common_activities_mapping = Agg.aggregate_IOT_and_activities_mapping(IOT_CO2,
                                                                                      aggregation_items,
                                                                                      common_activities_mapping)
    CO2_activities_mapping = ldl.extend_activities_mapping(study_dashb['studydata_dir'] / 'CO2_activities_mapping.csv',
                                                           IOT_CO2,
                                                           common_activities_mapping)
    CO2_activities_coord = ldl.get_categories_coordinates(study_dashb['studydata_dir'] / 'CO2_categories_coordinates.csv',
                                                          CO2_activities_mapping)
    return ldl.extract_IOTs_from(IOT_CO2,
                                 CO2_activities_coord)


def get_labour(study_dashb: Dict[str, str],
               aggregation_items: (Dict[str, List[str]],
                                   Dict[str, str])
               ) -> pd.Series:
    IOT_labour = cu.read_table(study_dashb['studydata_dir'] / 'Labour.csv',
                               delimiter=file_delimiter,
                               skipfooter=1,
                               engine='python')
    if Agg.is_aggregation(aggregation_items):
        keys_aggregation, values_aggregation = aggregation_items
        IOT_labour = Agg.aggregate_IOT(IOT_labour,
                                       keys_aggregation)
    return IOT_labour


def get_demography(study_dashb: Dict[str, str]
                   ) -> Dict[str, float]:
    demography_table = cu.read_table(study_dashb['studydata_dir'] / 'Demography.csv',
                                     delimiter=file_delimiter,
                                     skipfooter=1,
                                     engine='python')
    to_extract_demography = {line: demography_table.columns[0] for line in demography_table.index}
    return ldl.pick_selection(demography_table,
                              to_extract_demography)


def get_import_rates(study_dashb: Dict[str, str],
                     IOT_val_disagg: pd.DataFrame,
                     aggregation_items: (Dict[str, List[str]],
                                         Dict[str, str]),
                     value_coord: Dict[str, Coordinates]
                     ) -> Dict[str, pd.DataFrame]:
    IOT_import_rate = cu.read_table(study_dashb['studydata_dir'] / 'IOT_Import_rate.csv',
                                    delimiter=file_delimiter)
    IOT_import_value = IOT_import_rate.multiply(IOT_val_disagg)
    if Agg.is_aggregation(aggregation_items):
        keys_aggregation, values_aggregation = aggregation_items
        IOT_import_value = Agg.aggregate_IOT(IOT_import_value,
                                             keys_aggregation)
    import_value_coord = ldl.map_list_to_dict(use_categories, value_coord)
    import_value_coord = ldl.disaggregate_in_coordinates(import_value_coord,
                                                         ['FC'], 'IC')
    return ldl.extract_IOTs_from(IOT_import_value,
                                 import_value_coord)


def get_CO2_tax(quantity_coord: Dict[str, Tuple[List[str], List[str]]]
                ) -> Dict[str, pd.DataFrame]:
    # FIXME, might be best to define CO2_tax coordinates according to Commodities and Consumption
    CO2_tax_index, CO2_tax_columns = get_CO2_tax_indexes(quantity_coord)
    return pd.DataFrame(np.zeros((len(CO2_tax_index), len(CO2_tax_columns))),
                        index=CO2_tax_index,
                        columns=CO2_tax_columns)


def get_CO2_tax_indexes(quantity_coord: Dict[str, Tuple[List[str], List[str]]]
                        ) -> Tuple[List[str], List[str]]:
    CO2_tax_index = quantity_coord['IC'][0]
    final_consumption_columns = quantity_coord['FC'][1]
    government_index = final_consumption_columns.index('G')
    CO2_tax_columns = quantity_coord['IC'][1] + final_consumption_columns[:government_index]
    return CO2_tax_index, CO2_tax_columns
