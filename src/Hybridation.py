# coding : utf-8

import pandas as pd
import numpy as np
from typing import (Dict, List, Union)
from src.parameters import (IOT_balance_tolerance, linebreaker)

nonhybrid_p_value = 1000.


def get_hybrid_prices(study_dashb: Dict[str, str],
                      values_activities_mapping: Dict[str, List[str]],
                      Initial_quantities: Dict[str, Union[pd.DataFrame, pd.Series]],
                      Initial_values: Dict[str, Union[pd.DataFrame, pd.Series]]
                      ) -> Dict[str, pd.DataFrame]:
    hybrided_prices = dict()
    output_Initial_prices = dict()
    sectors = values_activities_mapping['Commodities']
    nonhybrid_sectors = values_activities_mapping['NonHybridCommod']
    hybrid_sectors = values_activities_mapping['HybridCommod']
    enersect_sectors = values_activities_mapping['EnerSect']
    prices = get_p(nonhybrid_sectors,
                   Initial_quantities,
                   Initial_values)
    output_Initial_prices['p'] = prices
    # Hypothesis for non hybrid commodities
    for MY in ['M', 'Y']:
        pMY = zeros_series_filled(sectors,
                                  nonhybrid_sectors,
                                  nonhybrid_p_value,
                                  MY)
        Initial_quantities[MY].update((Initial_values[MY].divide(pMY)).loc[nonhybrid_sectors])
        output_Initial_prices[MY] = pMY
    # Transport and trade margin rates
    gross_value = Initial_values['Y'].add(Initial_values['M'])
    for margin in ['Transp_margins', 'Trade_margins']:
        margin_rates = margin + '_rate'
        hybrided_prices[margin_rates] = Initial_values[margin].divide(gross_value)
    trans_trade_margins = hybrided_prices['Transp_margins_rate'].add(hybrided_prices['Trade_margins_rate'])
    # Price before all taxes
    p_BeforeTaxes = output_Initial_prices['p'].multiply(trans_trade_margins + 1)
    # Energy tax rate intermediate consumption
    Energy_Tax_rate_IC = zeros_series(sectors)
    enersect_Energy_Tax_rate_IC = (Initial_values['Energy_Tax_IC'].divide(Initial_quantities['IC'].sum(axis='columns'))).loc[enersect_sectors]
    Energy_Tax_rate_IC.update(enersect_Energy_Tax_rate_IC)
    FC_netX = sum_df_elements_sum(Initial_quantities,
                                  ['C', 'G', 'I'])
    Energy_Tax_rate_FC = zeros_series(sectors)
    enersect_Energy_Tax_rate_FC = (Initial_values['Energy_Tax_FC'].divide(FC_netX.replace(0, 1))).loc[enersect_sectors]
    Energy_Tax_rate_FC.update(enersect_Energy_Tax_rate_FC)
    # Other tax product
    OtherIndirTax_rate = zeros_series(sectors)
    hybrid_OtherIndirTax_rate = (Initial_values['OtherIndirTax'].divide(sum_df_elements_sum(Initial_quantities,
                                                                                            ['IC', 'C', 'G', 'I']))).loc[hybrid_sectors]
    nonhybrid_OtherIndirTax_rate = (Initial_values['OtherIndirTax'].divide(Initial_quantities['Y'].add(Initial_quantities['M']).sub(Initial_quantities['X'].divide(p_BeforeTaxes)))).loc[nonhybrid_sectors]
    update_df(OtherIndirTax_rate,
              [hybrid_OtherIndirTax_rate, nonhybrid_OtherIndirTax_rate])
    # Price before Value_Added and Specific margins on intermediate consumption
    p_BeforeVAT_SpeMarg_IC = p_BeforeTaxes.add(Energy_Tax_rate_IC).add(OtherIndirTax_rate)
    # Price before Value_Added and Specific margins on finale consumption
    p_BeforeVAT_SpeMarg_FC = p_BeforeTaxes.add(Energy_Tax_rate_FC).add(OtherIndirTax_rate)
    if study_dashb['region'] == 'Brasil':
        # FIXME Brasil not finished initial_value.Cons_Tax unknown
        C_netX_value = sum_df_elements_sum(Initial_values,
                                           ['IC', 'C', 'G', 'I'])
    else:
        FC_netX_value = sum_df_elements_sum(Initial_values,
                                            ['C', 'G', 'I'])
        FC_netX_VAT_value = FC_netX_value.sub(Initial_values['VA_Tax'])
        Tax_rate = Initial_values['VA_Tax'].divide(FC_netX_VAT_value.replace(0, 1))
        p_AllTax_WithoutSpeM = p_BeforeVAT_SpeMarg_FC.multiply(Tax_rate + 1)
    # ///////////////////////////////////////////////////////////
    # // Calculation of unitary price
    # ///////////////////////////////////////////////////////////
    pIC = zeros_df(sectors)
    # FIXME, need to decide whether .multiply(Initial_quantities['IC'] != 0) is needed or the compatibility between Initial_values['IC'] and Initial_quantities['IC'] should be tested beforehand
    IC_quantities_nonzero_mask = Initial_quantities['IC'] != 0
    # FIXME Brasil not finished variables depend on previous block
    if study_dashb['region'] == 'Brasil':
        hybrid_pIC = ((Initial_values['IC'].multiply(IC_quantities_nonzero_mask)).divide(Initial_quantities['IC'].multiply(IC_quantities_nonzero_mask).replace(0, 1)))
    else:
        tiled_p_BeforeVAT_SpeMarg_IC = pd.concat([p_BeforeVAT_SpeMarg_IC.T] * len(sectors),
                                                 axis='columns').set_axis(sectors,
                                                                          axis='columns',
                                                                          inplace=False)
        hybrid_pIC = (((Initial_values['IC'].multiply(IC_quantities_nonzero_mask)).divide((Initial_quantities['IC'].multiply(IC_quantities_nonzero_mask).replace(0, 1)))).add(tiled_p_BeforeVAT_SpeMarg_IC.multiply(Initial_quantities['IC'] == 0))).loc[hybrid_sectors, :]
        nonhybrid_pIC = tiled_p_BeforeVAT_SpeMarg_IC.loc[nonhybrid_sectors, :]
    update_df(pIC, [hybrid_pIC, nonhybrid_pIC])
    output_Initial_prices['IC'] = pIC
    # pC/pI/pG = p_AllTax_WithoutSpeM for non hybrid commodities
    consumption_households_headers = Initial_quantities['C'].columns.tolist()
    pC = zeros_df(sectors, consumption_households_headers)
    C_quantities_nonzero_mask = Initial_quantities['C'] != 0
    tiled_p_AllTax_WithoutSpeM = pd.concat([p_AllTax_WithoutSpeM.T] * len(consumption_households_headers),
                                           axis='columns').set_axis(consumption_households_headers,
                                                                    axis='columns',
                                                                    inplace=False)
    hybrid_pC = (((Initial_values['C'].multiply(C_quantities_nonzero_mask)).divide((Initial_quantities['C'].multiply(C_quantities_nonzero_mask).replace(0, 1)))).add(tiled_p_AllTax_WithoutSpeM.multiply(Initial_quantities['C'] == 0))).loc[hybrid_sectors, :]
    nonhybrid_pC = tiled_p_AllTax_WithoutSpeM.loc[nonhybrid_sectors, :]
    update_df(pC, [hybrid_pC, nonhybrid_pC])
    output_Initial_prices['C'] = pC
    for GI in ['G', 'I']:
        pGI = zeros_series(sectors)
        GI_quantities_non_zero_mask = Initial_quantities[GI] != 0
        hybrid_pGI = (((Initial_values[GI].multiply(GI_quantities_non_zero_mask)).divide(Initial_quantities[GI].multiply(GI_quantities_non_zero_mask).replace(0, 1))).add(p_AllTax_WithoutSpeM.multiply(Initial_quantities[GI] == 0))).loc[hybrid_sectors]
        nonhybrid_pGI = p_AllTax_WithoutSpeM[nonhybrid_sectors]
        update_df(pGI, [hybrid_pGI, nonhybrid_pGI])
        output_Initial_prices[GI] = pGI.rename(GI)
    # Export price
    pX = zeros_series(sectors)
    X_quantities_non_zero_mask = Initial_quantities['X'] != 0
    # pX = Value/ Quantites, if quantities=0 then pX = p_BeforeTaxes for hybrid commodities
    hybrid_pX = (((Initial_values['X'].multiply(X_quantities_non_zero_mask)).divide(Initial_quantities['X'].multiply(X_quantities_non_zero_mask).replace(0, 1))).add(p_BeforeTaxes.multiply(Initial_quantities['X'] == 0))).loc[hybrid_sectors]
    # pX =  for non hybrid commodities
    nonhybrid_pX = p_BeforeTaxes[nonhybrid_sectors]
    update_df(pX, [hybrid_pX, nonhybrid_pX])
    output_Initial_prices['X'] = pX.rename('X')

    # pM/pY= Value/Quantites, if quantities=O then price= p
    M_quantities_nonzero_mask = Initial_quantities['M'] != 0
    hybrid_pM = (((Initial_values['M'].multiply(M_quantities_nonzero_mask)).divide((Initial_quantities['M'].multiply(M_quantities_nonzero_mask)).replace(0, 1))).add(prices.multiply((Initial_quantities['M'] == 0)))).loc[hybrid_sectors]
    output_Initial_prices['M'].update(hybrid_pM)
    Y_quantities_nonzero_mask = Initial_quantities['Y'] != 0
    hybrid_pY = (((Initial_values['Y'].multiply(Y_quantities_nonzero_mask)).divide((Initial_quantities['Y'].multiply(Y_quantities_nonzero_mask)).replace(0, 1))).add(((Initial_quantities['Y'] == 0).multiply(1E-10)))).loc[hybrid_sectors]
    output_Initial_prices['Y'].update(hybrid_pY)

    output_Initial_prices['FC'] = pd.concat([output_Initial_prices['C'],
                                             series_to_column_df(output_Initial_prices['G']),
                                             series_to_column_df(output_Initial_prices['I']),
                                             series_to_column_df(output_Initial_prices['X'])],
                                            axis='columns')
    # ///////////////////////////////////////////////////////////
    # //Calculation of specific margis rate
    # ///////////////////////////////////////////////////////////

    # SpeMarg_IC euro/toe en intermediate consumption
    pSpeMargIC = zeros_df(sectors)
    if study_dashb['region'] == 'Brasil':
        # FIXME Brasil not done
        hybrid_pSpeMargIC = pIC
    else:
        hybrid_pSpeMargIC = ((pIC.sub(tiled_p_BeforeVAT_SpeMarg_IC)).T).loc[:, hybrid_sectors]
    pSpeMargIC.update(hybrid_pSpeMargIC)
    SpeMarg_IC = pSpeMargIC.multiply(Initial_quantities['IC'].T)
    Initial_values['SpeMarg_IC'] = SpeMarg_IC.set_axis(Initial_values['SpeMarg_IC'].index,
                                                       axis='index',
                                                       inplace=False)

    # SpeMarg_C euro/toe en final consumption
    pSpeMargC = zeros_df(consumption_households_headers, sectors)
    hybrid_pSpeMargC = ((pC.T.sub(tiled_p_AllTax_WithoutSpeM.T)).divide(pd.concat([1 + Tax_rate] * len(consumption_households_headers)))).loc[:, hybrid_sectors]
    pSpeMargC.update(hybrid_pSpeMargC)
    SpeMarg_C = pSpeMargC.multiply(Initial_quantities['C'].T)
    Initial_values['SpeMarg_C'] = SpeMarg_C.set_axis(Initial_values['SpeMarg_C'].index,
                                                     axis='index',
                                                     inplace=False)

    # SpeMarg_I euro/toe en final consumption & SpeMarg_G
    if study_dashb['region'] == 'Brasil':
        pass
    else:
        pSpeMargI = zeros_series(sectors)
        hybrid_pSpeMargI = ((output_Initial_prices['I'].sub(p_AllTax_WithoutSpeM)).divide(1 + Tax_rate)).loc[hybrid_sectors]
        pSpeMargI.update(hybrid_pSpeMargI)
        SpeMarg_I = pSpeMargI.multiply(Initial_quantities['I'])
        Initial_values['SpeMarg_I'] = SpeMarg_I.rename('SpeMarg_I')

        Initial_values['SpeMarg_G'] = zeros_series(sectors, 'SpeMarg_G')

    pSpeMargX = zeros_series(sectors)
    hybrid_pSpeMargX = output_Initial_prices['X'].sub(p_BeforeTaxes)
    pSpeMargX.update(hybrid_pSpeMargX.loc[hybrid_sectors])
    SpeMargX = pSpeMargX.multiply(Initial_quantities['X'])
    Initial_values['SpeMarg_X'] = SpeMargX.rename('SpeMarg_X')

    # Total margins

    Initial_values['Total_SpeMarg'] = sum_df_elements_sum(Initial_values,
                                                          ['SpeMarg_IC', 'SpeMarg_C'],
                                                          'index').add(Initial_values['SpeMarg_G']).add(Initial_values['SpeMarg_I']).add(Initial_values['SpeMarg_X'])
    Initial_values['SpeMarg_FC'] = pd.concat([Initial_values['SpeMarg_C'],
                                              series_to_row_df(Initial_values['SpeMarg_G']),
                                              series_to_row_df(Initial_values['SpeMarg_I']),
                                              series_to_row_df(Initial_values['SpeMarg_X'])])
    Initial_values['SpeMarg'] = pd.concat([Initial_values['SpeMarg_IC'],
                                           Initial_values['SpeMarg_FC']])
    Initial_values['OthPart_IOT'] = pd.concat([Initial_values['Value_Added'],
                                               series_to_row_df(Initial_values['M']),
                                               Initial_values['Margins'],
                                               Initial_values['SpeMarg'],
                                               Initial_values['Taxes']])
    Initial_values['tot_OthPart_IOT'] = Initial_values['OthPart_IOT'].sum(axis='index')

    print("===============================================" + linebreaker)
    print("test equilibrium on specific margins after hybridization" + linebreaker)
    print("===============================================" + linebreaker)

    SpeMarg_sum = Initial_values['SpeMarg'].sum(axis='index')
    for activity in SpeMarg_sum.index:
        activity_SpeMarg_sum = SpeMarg_sum[activity]
        if abs(activity_SpeMarg_sum) > IOT_balance_tolerance:
            print(activity + " to balance: " + str(activity_SpeMarg_sum) + linebreaker)
    return output_Initial_prices


def get_p(nonhybrid_sectors: List[str],
          Initial_quantities: Dict[str, Union[pd.DataFrame, pd.Series]],
          Initial_values: Dict[str, Union[pd.DataFrame, pd.Series]]) -> pd.Series:
    hydrid_value = Initial_values['IC'].sum(axis='index') + \
                   Initial_values['Value_Added'].sum(axis='index') + \
                   Initial_values['M']
    hydrid_quantity = Initial_quantities['IC'].sum(axis='columns') + \
                      Initial_quantities['FC'].sum(axis='columns')
    hybrid_p = hydrid_value.divide(hydrid_quantity.T)
    return fill_in(hybrid_p.squeeze(),
                   nonhybrid_sectors,
                   nonhybrid_p_value,
                   'p')


def fill_in(entry_series: pd.Series,
            to_fill_headers: List[str],
            fill_value: Union[int, float],
            name: str
            ) -> pd.DataFrame:
    condition_mapping = np.isin(entry_series.index, to_fill_headers)
    # the ~ operator is a unary invert operator to conform to where usage
    filled_series = entry_series.where(~condition_mapping,
                                       fill_value)
    return filled_series.rename(name)


def zeros_series_filled(entry_headers: List[str],
                        to_fill_headers: List[str],
                        fill_value: Union[int, float],
                        name: str
                        ) -> pd.DataFrame:
    full_zeros_series = zeros_series(entry_headers)
    return fill_in(full_zeros_series,
                   to_fill_headers,
                   nonhybrid_p_value,
                   name)


def zeros_series(entry_index: List,
                 name: Union[str, None] = None
                 ) -> pd.Series:
    output_series = pd.Series(np.zeros(len(entry_index)),
                              index=entry_index)
    if name is not None:
        return output_series.rename(name)
    return output_series


def sum_df_elements_sum(input_values: Dict[str, Union[pd.Series, pd.DataFrame]],
                        elements: List[str],
                        axis: str = 'columns'
                        ) -> pd.Series:
    out_series = get_results_zeros_series(input_values[elements[0]],
                                          axis)
    for element in elements:
        to_add_frame_series = input_values[element]
        if isinstance(to_add_frame_series, pd.DataFrame):
            out_series = out_series.add(to_add_frame_series.sum(axis=axis))
        else:
            out_series = out_series.add(to_add_frame_series)
    return out_series


def get_results_zeros_series(ref_IOT: pd.DataFrame,
                             axis: str) -> pd.Series:
    if axis == 'columns':
        return zeros_series(ref_IOT.index.tolist())
    return zeros_series(ref_IOT.columns.tolist())


def update_df(input_df: pd.DataFrame,
              updates_df: List[pd.DataFrame]
              ) -> pd.DataFrame:
    for update_df in updates_df:
        input_df.update(update_df)


def zeros_df(index: List[str],
             columns: Union[List[str], None] = None,
             ) -> pd.DataFrame:
    if not columns:
        columns = index
    return pd.DataFrame(np.zeros((len(index), (len(columns)))),
                        index=index,
                        columns=columns)


def series_to_column_df(entry_series: pd.Series,
                        name: Union[str, None] = None):
    if entry_series.name:
        name = entry_series.name
    return entry_series.to_frame(name)


def series_to_row_df(entry_series: pd.Series,
                     name: Union[str, None] = None):
    return series_to_column_df(entry_series,
                               name=name).T
