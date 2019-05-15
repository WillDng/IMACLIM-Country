# coding : utf-8

import pandas as pd
import numpy as np
from typing import (Dict, List, Union)

non_hybrid_p_value = 1000.


def get_hybrid_prices(values_activities_mapping: Dict[str, List[str]],
                      Initial_quantities: Dict[str, Union[pd.DataFrame, pd.Series]],
                      Initial_values: Dict[str, Union[pd.DataFrame, pd.Series]]
                      ) -> Dict[str, pd.DataFrame]:
    hybrided_prices = dict()
    hybrided_prices['p'] = get_p(values_activities_mapping,
                                 Initial_quantities,
                                 Initial_values)
    filled_zeros_column_non_hybrid = ['pM', 'pY']
    for price in filled_zeros_column_non_hybrid:
        hybrided_prices[price] = filled_zeros_column_dataframe(values_activities_mapping['Commodities'],
                                                               values_activities_mapping['NonHybridCommod'],
                                                               non_hybrid_p_value,
                                                               price)
    return hybrided_prices


def get_p(values_activities_mapping: Dict[str, List[str]],
          Initial_quantities: Dict[str, Union[pd.DataFrame, pd.Series]],
          Initial_values: Dict[str, Union[pd.DataFrame, pd.Series]]) -> pd.Series:
    hydrid_value = Initial_values['IC'].sum(axis='index') + \
                   Initial_values['Value_Added'].sum(axis='index') + \
                   Initial_values['M']
    hydrid_quantity = Initial_quantities['IC'].sum(axis='columns') + \
                      Initial_quantities['FC'].sum(axis='columns')
    hybrid_p = hydrid_value.divide(hydrid_quantity.T)
    return fill_in(hybrid_p.squeeze(),
                   values_activities_mapping['NonHybridCommod'],
                   non_hybrid_p_value,
                   'p').T


def fill_in(entry_series: pd.Series,
            to_fill_headers: List[str],
            fill_value: Union[int, float],
            name: str
            ) -> pd.DataFrame:
    condition_mapping = np.isin(entry_series.index, to_fill_headers)
    # the ~ operator is a unary invert operator to conform to where usage
    filled_series = entry_series.where(~condition_mapping,
                                       fill_value)
    return filled_series.to_frame(name)


def filled_zeros_column_dataframe(entry_headers: List[str],
                                  to_fill_headers: List[str],
                                  fill_value: Union[int, float],
                                  name: str
                                  ) -> pd.DataFrame:
    full_zeros_series = zeros_series(entry_headers)
    return fill_in(full_zeros_series,
                   to_fill_headers,
                   non_hybrid_p_value,
                   name)


def zeros_series(entry_index: List,
                 name: Union[str, None] = None
                 ) -> pd.Series:
    output_series = pd.Series(np.zeros(len(entry_index)),
                              index=entry_index)
    if name is not None:
        return output_series.rename(name)
    return output_series
