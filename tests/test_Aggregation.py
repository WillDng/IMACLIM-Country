# coding : utf-8

from src import Aggregation


def test_complete_missing_keys():
    headers = ['a', 'b', 'c', 'd']
    dict_to_complete = {'a':'b', 'e':'f', 'i':'j'}
    expected_completed_dict = {'a':'b', 'e':'f', 'i':'j',
                               'b':'b', 'c':'c', 'd':'d'}
    assert Aggregation.complete_missing_keys(dict_to_complete, headers)


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
    assert set(Aggregation.aggregate_in_list(list_to_aggregate,
                                             aggregation_mapping)) == set(expected_aggregated_list)

