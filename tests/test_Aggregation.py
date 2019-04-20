# coding : utf-8

import pandas as pd
from src import Aggregation


def test_complete_missing_keys():
    headers = ['a', 'b', 'c', 'd']
    dict_to_complete = {'a': 'z', 'e': 'f', 'i': 'j'}
    expected_completed_dict = {'a': 'z', 'e': 'f', 'i': 'j',
                               'b': 'b', 'c': 'c', 'd': 'd'}
    assert Aggregation.complete_missing_keys(dict_to_complete, headers) == expected_completed_dict


list_to_aggregate = ['Crude_oil', 'Natural_gas', 'Coking_coal', 'Bituminous_coal',
                     'Coke', 'Other_coal', 'Gasoline', 'LPG', 'Jetfuel', 'Fuel',
                     'Fuel_oil', 'Heavy_fuel_oil', 'Other_fuel_prod', 'Electricity',
                     'HeatGeoSol_Th', 'Steel_Iron', 'NonFerrousMetals', 'Cement',
                     'OthMin', 'Buildings_constr', 'Work_constr', 'ChemicalPharma',
                     'Paper', 'Mining', 'Automobile', 'OthTranspEquip', 'Load_PipeTransp',
                     'PassTransp', 'NavalTransp', 'AirTransp', 'Agri_Forestry',
                     'Fishing', 'Food_industry', 'Property_business', 'Comp']
aggregation_mapping = {'Crude_oil': ['Crude_oil'], 'Natural_gas': ['Natural_gas'],
                       'Coal': ['Coking_coal', 'Bituminous_coal', 'Coke', 'Other_coal'],
                       'AllFuels': ['Gasoline', 'LPG', 'Jetfuel', 'Fuel', 'Fuel_oil', 'Heavy_fuel_oil', 'Other_fuel_prod'],
                       'Electricity': ['Electricity'],
                       'HeatGeoSol_Th': ['HeatGeoSol_Th'],
                       'Heavy_Industry': ['Steel_Iron', 'NonFerrousMetals', 'Cement', 'OthMin', 'ChemicalPharma', 'Paper', 'Mining'],
                       'Buildings_constr': ['Buildings_constr'],
                       'Work_constr': ['Work_constr'],
                       'Automobile': ['Automobile'],
                       'OthSectors': ['OthTranspEquip', 'NavalTransp', 'AirTransp', 'Comp'],
                       'Load_PipeTransp': ['Load_PipeTransp'],
                       'PassTransp': ['PassTransp'],
                       'Agri_Food_industry': ['Agri_Forestry', 'Fishing', 'Food_industry'],
                       'Property_business': ['Property_business']}
expected_aggregated_list = ['Crude_oil', 'Natural_gas', 'Coal', 'AllFuels',
                            'Electricity', 'HeatGeoSol_Th', 'Heavy_Industry', 'Buildings_constr',
                            'Work_constr', 'Automobile', 'OthSectors', 'Load_PipeTransp',
                            'PassTransp', 'Agri_Food_industry', 'Property_business']


def test_aggregate_in_list():
    unordered_activities, remaining_activities = Aggregation.aggregate_in_list(list_to_aggregate,
                                                                               aggregation_mapping)
    unordered_activities += list(remaining_activities)
    assert set(unordered_activities) == set(expected_aggregated_list)


def test_treat_remaining():
    remaining_activities = ['Cement', 'NavalTransp', 'AirTransp', 'Steel_Iron',
                            'Paper', 'OthMin', 'Comp', 'Mining', 'NonFerrousMetals',
                            'ChemicalPharma', 'OthTranspEquip']
    values_aggregation = {'Crude_oil': ['Crude_oil'],
                          'Natural_gas': ['Natural_gas'],
                          'Coal': ['Coking_coal', 'Bituminous_coal', 'Coke', 'Other_coal'],
                          'AllFuels': ['Gasoline', 'LPG', 'Jetfuel', 'Fuel', 'Fuel_oil', 'Heavy_fuel_oil', 'Other_fuel_prod'],
                          'Electricity': ['Electricity'],
                          'HeatGeoSol_Th': ['HeatGeoSol_Th'],
                          'Heavy_Industry': ['Steel_Iron', 'NonFerrousMetals', 'Cement', 'OthMin', 'ChemicalPharma', 'Paper', 'Mining'],
                          'Buildings_constr': ['Buildings_constr'],
                          'Work_constr': ['Work_constr'],
                          'Automobile': ['Automobile'],
                          'OthSectors': ['OthTranspEquip', 'NavalTransp', 'AirTransp', 'Comp'],
                          'Load_PipeTransp': ['Load_PipeTransp'],
                          'PassTransp': ['PassTransp'],
                          'Agri_Food_industry': ['Agri_Forestry', 'Fishing', 'Food_industry'],
                          'Property_business': ['Property_business']}
    partial_agg_activities_mapping = {'HybridCommod': ['Crude_oil', 'Natural_gas', 'Coal', 'AllFuels',
                                                       'Electricity', 'HeatGeoSol_Th', 'Automobile', 'Load_PipeTransp',
                                                       'PassTransp', 'Property_business'],
                                      'NonHybridCommod': ['Buildings_constr', 'Work_constr', 'Agri_Food_industry']}
    ordering_header = pd.Index(['Crude_oil', 'Natural_gas', 'Coal', 'AllFuels', 'Electricity',
                                'HeatGeoSol_Th', 'Heavy_Industry', 'Buildings_constr', 'Work_constr',
                                'Automobile', 'OthSectors', 'Load_PipeTransp', 'PassTransp',
                                'Agri_Food_industry', 'Property_business', 'Labour_income',
                                'Labour_Tax', 'Capital_income', 'Production_Tax', 'Profit_margin',
                                'M_value', 'Trade_margins', 'Transp_margins', 'SpeMarg_Crude_oil',
                                'SpeMarg_Natural_gas', 'SpeMarg_Coking_coal', 'SpeMarg_Bituminous_coal',
                                'SpeMarg_Coke', 'SpeMarg_Other_coal', 'SpeMarg_Gasoline', 'SpeMarg_LPG',
                                'SpeMarg_Jetfuel', 'SpeMarg_Fuel', 'SpeMarg_Fuel_oil',
                                'SpeMarg_Heavy_fuel_oil', 'SpeMarg_Other_fuel_prod',
                                'SpeMarg_Electricity', 'SpeMarg_HeatGeoSol_Th', 'SpeMarg_Steel_Iron',
                                'SpeMarg_NonFerrousMetals', 'SpeMarg_Cement', 'SpeMarg_OthMin',
                                'SpeMarg_Buildings_constr', 'SpeMarg_Work_constr',
                                'SpeMarg_ChemicalPharma', 'SpeMarg_Paper', 'SpeMarg_Mining',
                                'SpeMarg_Automobile', 'SpeMarg_OthTranspEquip',
                                'SpeMarg_Load_PipeTransp', 'SpeMarg_PassTransp', 'SpeMarg_NavalTransp',
                                'SpeMarg_AirTransp', 'SpeMarg_Agri_Forestry', 'SpeMarg_Fishing',
                                'SpeMarg_Food_industry', 'SpeMarg_Property_business', 'SpeMarg_Comp',
                                'SpeMarg_C', 'SpeMarg_G', 'SpeMarg_I', 'SpeMarg_X', 'VA_Tax',
                                'Energy_Tax_IC', 'Energy_Tax_FC', 'ClimPolCompensbySect',
                                'OtherIndirTax'],
                               dtype='object')
    new_aggregated_mapping = Aggregation.treat_remaining('Hybrid',
                                                         remaining_activities,
                                                         values_aggregation,
                                                         partial_agg_activities_mapping,
                                                         ordering_header)
    expected_agg_activities_mapping = {'HybridCommod': ['Crude_oil', 'Natural_gas', 'Coal', 'AllFuels',
                                                        'Electricity', 'HeatGeoSol_Th', 'Automobile', 'Load_PipeTransp',
                                                        'PassTransp', 'Property_business'],
                                       'NonHybridCommod': ['Heavy_Industry', 'Buildings_constr', 'Work_constr',
                                                           'OthSectors', 'Agri_Food_industry']}
    assert new_aggregated_mapping == expected_agg_activities_mapping
