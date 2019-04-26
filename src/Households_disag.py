# coding : utf-8

import pandas as pd
from typing import (Dict, Iterable, List, Union)
from src import common_utils as cu
from src.parameters import file_delimiter


def read_disaggregation(study_dashb: Dict[str, str]
                        ) -> pd.DataFrame:
    chosen_disaggregation = study_dashb.get('H_DISAGG', None)
    if chosen_disaggregation is None:
        return None
    disaggregation_rate_dir = study_dashb['disaggregation_dir'] / 'rate'
    disaggregation_level_rate = 'IOT_rate_' + chosen_disaggregation + '.csv'
    return cu.read_table(disaggregation_rate_dir / disaggregation_level_rate,
                         delimiter=file_delimiter)


def get_households(chosen_disaggregation: str
                   ) -> List[str]:
    households_prefix = 'H'
    disaggregation_level = chosen_disaggregation.lstrip(households_prefix)
    households_list = [households_prefix + str(i) for i in range(1, int(disaggregation_level) + 1)]
    return households_list


def modify_account_table_mapping(account_table_mapping: Dict[str, List[str]],
                                 disaggregation_classes: pd.Index
                                 ) -> None:
    disaggregation_classes = disaggregation_classes.tolist()
    account_table_mapping['Households'] = disaggregation_classes
    accounts_mapping_to_extend = ['DomesticAgents', 'InstitAgents']
    for account_mapping_to_extend in accounts_mapping_to_extend:
        account_table_mapping[account_mapping_to_extend].extend(disaggregation_classes)


def disaggregate_account_table(institution_to_disaggregate: str,
                               account_data: pd.DataFrame,
                               distribution_key: pd.DataFrame,
                               accounts_mapping: Dict[str, List[str]],
                               item_normalize_onto: Union[str, None] = None
                               ) -> pd.DataFrame:
    disaggregated_households = disaggregate_column_non_round_erred(institution_to_disaggregate,
                                                                   account_data,
                                                                   distribution_key,
                                                                   fill_value=0.,
                                                                   item_normalize_onto=item_normalize_onto)

    modify_households(disaggregated_households,
                      accounts_mapping)
    return replace_disaggregated_column(institution_to_disaggregate,
                                        account_data,
                                        disaggregated_households)


def disaggregate_column_non_round_erred(item_to_disaggregate: str,
                                        to_disaggregate_table: pd.DataFrame,
                                        distribution_key: pd.DataFrame,
                                        fill_value: Union[float, None] = 0.,
                                        item_normalize_onto: Union[str, None] = None
                                        ) -> pd.DataFrame:
    round_erred_table = disaggregate_column(item_to_disaggregate,
                                            to_disaggregate_table,
                                            distribution_key,
                                            fill_value=fill_value)
    return normalize_error_in_disaggregation(round_erred_table,
                                             item_normalize_onto,
                                             to_disaggregate_table.loc[:, item_to_disaggregate])


def disaggregate_column(item_to_disaggregate: str,
                        to_disaggregate_table: pd.DataFrame,
                        distribution_key: pd.DataFrame,
                        fill_value: Union[float, None] = 0.
                        ) -> pd.DataFrame:
    disaggregated_households = distribution_key.multiply(to_disaggregate_table.loc[:, item_to_disaggregate],
                                                         axis='index')
    disaggregated_households = fill_na(disaggregated_households,
                                       fill_value,
                                       distribution_key)
    return disaggregated_households.reindex(index=to_disaggregate_table.index)


def fill_na(IOT_to_fill: pd.DataFrame,
            fill_value: Union[float, None],
            distribution_key: pd.DataFrame
            ) -> pd.DataFrame:
    # FIXME should apply to share rate not to final results
    fill_value = get_mistmatched_fill_value(fill_value,
                                            distribution_key)
    return IOT_to_fill.fillna(fill_value)


def get_mistmatched_fill_value(fill_value: Union[float, None],
                               distribution_key: pd.DataFrame
                               ) -> None:
    if fill_value is None:
        fill_value = 1. / len(distribution_key.columns)
    return fill_value


def normalize_error_in_disaggregation(disaggregated_erred_table: pd.DataFrame,
                                      item_normalize_onto: Union[str, None],
                                      reference: pd.Series
                                      ) -> pd.DataFrame:
    item_normalize_onto, remaining_headers = identify_normalization_items(disaggregated_erred_table,
                                                                          item_normalize_onto)
    remaining_headers_sum = disaggregated_erred_table.loc[:, remaining_headers].sum(axis='columns')
    modified_disaggregated_table = disaggregated_erred_table.copy()
    modified_disaggregated_table[item_normalize_onto] = reference - remaining_headers_sum
    return modified_disaggregated_table


def identify_normalization_items(disaggregated_erred_table: pd.DataFrame,
                                 item_normalize_onto: Union[str, None],
                                 ) -> (str, List[str]):
    remaining_headers = disaggregated_erred_table.columns.tolist()
    if not item_normalize_onto:
        item_normalize_onto = remaining_headers.pop()
    else:
        item_normalize_onto = remaining_headers.pop(remaining_headers.index(item_normalize_onto))
    return item_normalize_onto, remaining_headers


def replace_disaggregated_column(activity_to_disaggregate: str,
                                 IOT_insert_into: pd.DataFrame,
                                 disaggregated_activity_table: pd.DataFrame,
                                 fill_value: Union[float, None] = 0.,
                                 ) -> pd.DataFrame:
    # FIXME might be more efficicient to directly concat DataFrames
    #       IOT_insert_into[:,[:index(activity_to_disaggregate)]] + disaggregated_activity_table + IOT_insert_into[:, [index(activity_to_disaggregate)+1:]]
    concatenated_IOT = pd.concat([IOT_insert_into, disaggregated_activity_table],
                                 axis='columns',
                                 sort=False)
    if ((concatenated_IOT.isna().values.any()) and
        (fill_value is not None)):
        concatenated_IOT = concatenated_IOT.fillna(fill_value)
    new_IOT_header = get_disaggregated_header(activity_to_disaggregate,
                                              IOT_insert_into.columns,
                                              disaggregated_activity_table.columns)
    activity_dropped_concatenated_IOT = concatenated_IOT.drop(activity_to_disaggregate,
                                                              axis='columns')
    return activity_dropped_concatenated_IOT.reindex(columns=new_IOT_header)


def get_disaggregated_header(item_to_replace: str,
                             original_header: pd.Index,
                             headers_to_insert: pd.Index
                             ) -> List[str]:
    original_list = original_header.tolist()
    item_to_replace_index = original_list.index(item_to_replace)
    return original_list[:item_to_replace_index] + \
           headers_to_insert.tolist() + \
           original_list[item_to_replace_index + 1:]


def modify_households(households_table: pd.DataFrame,
                      accounts_mapping: Dict[str, List[str]]):
    # FIXME As 'NetLending' is calculated based on updated values of households table, get_modified_values()
    #       allows to on-demand calculate modifications values, as such, accounts to modify list has to match
    #       households_modifications keys (because )

    def get_modified_values(account: Union[str, None],
                            current_households_table: pd.DataFrame
                            ) -> pd.Series:
        households_modifications = {'Disposable_Income': ((current_households_table.loc[accounts_mapping['H_Income'], :].sum()) -
                                                          (current_households_table.loc[accounts_mapping['H_Tax'], :].apply(abs).sum())),
                                    'Tot_FC_byAgent': (current_households_table.loc['FC_byAgent'] +
                                                       current_households_table.loc['GFCF_byAgent']),
                                    'NetLending': (current_households_table.loc['Disposable_Income'] -
                                                   current_households_table.loc['Tot_FC_byAgent'])}
        if not account:
            return households_modifications.keys()
        return households_modifications[account]

    accounts_to_modify = get_modified_values(None, households_table)
    for account in accounts_to_modify:
        new_values = get_modified_values(account,
                                         households_table)
        update_row(account,
                   households_table,
                   new_values)


def update_row(index_to_update: str,
               dataframe_to_update: pd.DataFrame,
               series_to_put: pd.Series
               ) -> None:
    dataframe_to_put = series_to_put.to_frame(index_to_update)
    dataframe_to_update.update(dataframe_to_put.T)


def disaggregate_IOT_prices(activity_to_disaggregate: str,
                            IOT: pd.DataFrame,
                            distribution_key: pd.DataFrame
                            ) -> pd.DataFrame:
    disaggregated_activity = disaggregate_column_non_round_erred(activity_to_disaggregate,
                                                                 IOT,
                                                                 distribution_key.replace(distribution_key, 1.),
                                                                 fill_value=0.)
    return replace_disaggregated_column(activity_to_disaggregate,
                                        IOT,
                                        disaggregated_activity)


def disaggregate_IOT_values(activity_to_disaggregate: str,
                            IOT_values: pd.DataFrame,
                            distribution_key: pd.DataFrame,
                            disag_IOT_quantities: pd.DataFrame,
                            disag_IOT_prices: pd.DataFrame,
                            fill_value: Union[float, None] = 0.,
                            item_normalize_onto: Union[str, None] = None

                            ) -> pd.DataFrame:
    disaggregated_column_activity = disaggregate_value_column(disag_IOT_quantities,
                                                              disag_IOT_prices,
                                                              distribution_key,
                                                              fill_value=fill_value)
    disaggregated_column_IOT_values = replace_disaggregated_column(activity_to_disaggregate,
                                                                   IOT_values,
                                                                   disaggregated_column_activity,
                                                                   fill_value=fill_value)

    SpeMarg_to_disaggregate = 'SpeMarg_' + activity_to_disaggregate
    disaggregated_row_activity = disaggregate_row_non_round_erred(SpeMarg_to_disaggregate,
                                                                  disaggregated_column_IOT_values,
                                                                  distribution_key,
                                                                  fill_value=fill_value,
                                                                  item_normalize_onto=item_normalize_onto)
    return replace_disaggregated_row(SpeMarg_to_disaggregate,
                                     disaggregated_column_IOT_values,
                                     disaggregated_row_activity,
                                     fill_value=fill_value)


def disaggregate_value_column(disag_IOT_quantities: pd.DataFrame,
                              disag_IOT_prices: pd.DataFrame,
                              distribution_key: pd.DataFrame,
                              fill_value: Union[float, None] = 0.
                              ) -> pd.DataFrame:
    disaggregated_IOT_values = disag_IOT_quantities.multiply(disag_IOT_prices)
    disaggregated_value = disaggregated_IOT_values.reindex(index=distribution_key.index,
                                                           columns=distribution_key.columns)
    return fill_na(disaggregated_value,
                   fill_value,
                   distribution_key)


def disaggregate_IOT(activity_to_disaggregate: str,
                     IOT: pd.DataFrame,
                     distribution_key: pd.DataFrame,
                     fill_value: Union[float, None] = 0.,
                     item_normalize_onto: Union[str, None] = None
                     ) -> pd.DataFrame:
    disaggregated_activity = disaggregate_column_non_round_erred(activity_to_disaggregate,
                                                                 IOT,
                                                                 distribution_key,
                                                                 fill_value=fill_value,
                                                                 item_normalize_onto=item_normalize_onto)
    return replace_disaggregated_column(activity_to_disaggregate,
                                        IOT,
                                        disaggregated_activity)


def disaggregate_row_non_round_erred(item_to_disaggregate: str,
                                     to_disaggregate_table: pd.DataFrame,
                                     distribution_key: pd.DataFrame,
                                     fill_value: Union[float, None] = 0.,
                                     item_normalize_onto: Union[str, None] = None
                                     ) -> pd.DataFrame:
    return disaggregate_column_non_round_erred(item_to_disaggregate,
                                               to_disaggregate_table.T,
                                               distribution_key,
                                               fill_value=fill_value,
                                               item_normalize_onto=item_normalize_onto).T


def replace_disaggregated_row(activity_to_disaggregate: str,
                              IOT_insert_into: pd.DataFrame,
                              disaggregated_activity_table: pd.DataFrame,
                              fill_value: Union[float, None] = 0.
                              ) -> pd.DataFrame:
    return replace_disaggregated_column(activity_to_disaggregate,
                                        IOT_insert_into.T,
                                        disaggregated_activity_table.T,
                                        fill_value=fill_value).T


def replace_disaggregated_in_(entry_dictionnary: Dict[str, Union[str, Iterable[str]]],
                              item_to_replace: str,
                              item_to_replace_with: pd.Index
                              ) -> Iterable:
    replaced_dictionnary = dict()
    substitution_dictionnary = dict()
    substitution_dictionnary[item_to_replace] = item_to_replace_with.tolist()
    for key, value in entry_dictionnary.items():
        replaced_dictionnary[key] = substitute_dict_value(value,
                                                          substitution_dictionnary)
    return replaced_dictionnary


def substitute_dict_value(entry_value: Union[List[str], str],
                          substitution_dictionnary: Dict[str, str]
                          ) -> Union[List[str], str]:
    def substitute_if(value):
        return substitution_dictionnary.get(value, value)
    if isinstance(entry_value, list):
        return list(cu.flatten_list(map(substitute_if, entry_value)))
    return substitute_if(entry_value)
