# coding : utf-8

import pandas as pd
from typing import (Dict, List, Union)


def disaggregate_account_table(institution_to_disaggregate: str,
                               account_data: pd.DataFrame,
                               distribution_key: pd.DataFrame,
                               item_normalize_onto: str,
                               accounts_mapping: Dict[str, List[str]]
                               ) -> pd.DataFrame:
    disaggregated_households = disaggregate_column_non_round_erred(institution_to_disaggregate,
                                                                   account_data,
                                                                   distribution_key,
                                                                   item_normalize_onto)

    modify_households(disaggregated_households,
                      accounts_mapping)
    return replace_disaggregated_column(institution_to_disaggregate,
                                        account_data,
                                        disaggregated_households)

# def check_aggregation_files_adequation(account_data: pd.DataFrame,
#                                        ):


def disaggregate_column(item_to_disaggregate: str,
                        to_disaggregate_table: pd.DataFrame,
                        distribution_key: pd.DataFrame
                        ) -> pd.DataFrame:
    disaggregated_households = distribution_key.multiply(to_disaggregate_table.loc[:, item_to_disaggregate],
                                                         axis='index')
    fill_value = 0.
    disaggregated_households = disaggregated_households.fillna(fill_value)
    return disaggregated_households.reindex(to_disaggregate_table.index,
                                            index='index')


def disaggregate_column_non_round_erred(item_to_disaggregate: str,
                                        to_disaggregate_table: pd.DataFrame,
                                        distribution_key: pd.DataFrame,
                                        item_normalize_onto: str
                                        ) -> pd.DataFrame:
    round_erred_table = disaggregate_column(item_to_disaggregate,
                                            to_disaggregate_table,
                                            distribution_key)
    return normalize_error_in_disaggregation(round_erred_table,
                                             item_normalize_onto,
                                             to_disaggregate_table.loc[:, item_to_disaggregate])


def normalize_error_in_disaggregation(disaggregated_erred_table: pd.DataFrame,
                                      item_normalize_onto: str,
                                      reference: pd.Series
                                      ) -> pd.DataFrame:
    modified_disaggregated_table = disaggregated_erred_table.copy()
    remaining_headers = disaggregated_erred_table.columns.tolist()
    remaining_headers.remove(item_normalize_onto)
    new_item_values = reference - disaggregated_erred_table.loc[:, remaining_headers].sum(axis='columns')
    modified_disaggregated_table[item_normalize_onto] = new_item_values
    return modified_disaggregated_table


def replace_disaggregated_column(institution: str,
                                 account_data: pd.DataFrame,
                                 disaggregated_table: pd.DataFrame
                                 ) -> pd.DataFrame:
    concatenated_account_data = pd.concat([account_data, disaggregated_table],
                                          axis='columns')
    new_account_data_header = get_disaggregated_header(institution,
                                                       account_data.columns,
                                                       disaggregated_table.columns)
    institution_dropped_concatenated_account_data = concatenated_account_data.drop(institution,
                                                                                   axis='columns')
    return institution_dropped_concatenated_account_data.reindex(new_account_data_header,
                                                                 axis='columns')


def get_disaggregated_header(item_to_replace: 'str',
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
                                                                 distribution_key.replace(distribution_key, 1.))
    return replace_disaggregated_column(activity_to_disaggregate,
                                        IOT,
                                        disaggregated_activity)

