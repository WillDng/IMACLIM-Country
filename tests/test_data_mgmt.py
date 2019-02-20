# coding: utf-8

import numpy as np
import pytest
import pandas as pd
from code import data_mgmt
from code.data_mgmt import linebreaker

mock_data_dir = 'tests/mock_data/'
part_IOT_path = mock_data_dir+'IOT_part.csv'
IOT_delimiter = ';'

@pytest.fixture()
def part_IOT():
    IOT_uses = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X']
    IOT_ressources = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income']
    IOT_data = np.array([[0, 0, 0, 0, 19609.61370695],
                         [0, 0, 0, 0, 24190.37317909],
                         [0, 3225.19564403, 0, 0, 513333.19103917],
                         [0, 9044.45950877, 556606.98333951, 0, 0], 
                         [0, 20587.91760946, 1267005.36419441, 0, 0]])
    return pd.DataFrame(IOT_data, index=IOT_ressources, columns=IOT_uses)

def test_read_IOT_warns_when_bad_delimiter(capsys):
    data_mgmt.read_IOT(part_IOT_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : IOT delimiter might not be correctly informed in "+\
                            data_mgmt.get_filename_from(part_IOT_path)+\
                            linebreaker

@pytest.fixture()
def activities_mapping_part():
    return {'Commodities':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'OthPart_IOT':['Labour_income', 'Labour_Tax'],
            'Sectors':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'FC':['I', 'X'],
            'EnerSect':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'Value_Added':['Labour_income', 'Labour_Tax'],
            'NonSupplierSect':['Crude_oil', 'Natural_gas', 'Coking_coal']}

activities_mapping_part_file_path = mock_data_dir+'activities_mapping_part.csv'

def test_read_activities_mapping(activities_mapping_part):
    read_activities_mapping = data_mgmt.read_activities_mapping(activities_mapping_part_file_path, 
                                                                delimiter=';')
    assert read_activities_mapping == activities_mapping_part

def test_read_activities_mapping_warns_when_bad_delimiter(capsys):
    data_mgmt.read_activities_mapping(activities_mapping_part_file_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : delimiter might not be correctly informed in read_activities_mapping() for "+\
                            data_mgmt.get_filename_from(activities_mapping_part_file_path)+\
                            linebreaker

full_IOT_path = mock_data_dir+'IOT_Val.csv'

@pytest.fixture()
def full_IOT():
    return pd.read_csv(full_IOT_path, 
                           delimiter=IOT_delimiter,
                           index_col=0)

#FIXME might need to inform type of slice e.g:IC
def test_slice_warns_when_bad_activities_coordinates(full_IOT, capsys):
    bad_activities_coordinates = [['Coking_coal', 'I'], ['Natural_gas', 'Labour_Tax']]
    data_mgmt._slice(full_IOT, bad_activities_coordinates)
    captured = capsys.readouterr()
    assert captured.err == "Warning : activities coordinates might be ill informed"+\
                            linebreaker+str(bad_activities_coordinates)+\
                            ' returned empty values'+linebreaker

@pytest.fixture()
def categories_coordinates():
    categories_coordinates = {'IC':['Commodities','Sectors'],
                              'FC':['Commodities', 'FC'],
                              'OthPart_IOT':['OthPart_IOT', 'Sectors']}
    return categories_coordinates

def test_read_categories_coordinates(categories_coordinates):
    categories_coordinates_filepath = mock_data_dir + 'categories_coordinates.csv'
    read_categories_coordinates = data_mgmt.read_categories_coordinates_mapping(categories_coordinates_filepath)
    assert read_categories_coordinates == categories_coordinates

@pytest.fixture()
def ill_ordered_activities():
    return ['Natural_gas', 'Coking_coal', 'X', 'Crude_oil']

@pytest.fixture()
def IOT_part_headers():
    return [pd.Index(['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
                     dtype='object', name='Values'),
            pd.Index(['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X'], 
                     dtype='object')]

def test_get_matching_header_for(ill_ordered_activities, IOT_part_headers):
    assert data_mgmt._get_matching_header_for(ill_ordered_activities, IOT_part_headers).equals(IOT_part_headers[1])

def test_change_order_of(ill_ordered_activities, IOT_part_headers):
    assert data_mgmt._change_order_of(ill_ordered_activities, 
                                      IOT_part_headers[1]) == ['Coking_coal', 'Crude_oil', 'Natural_gas', 'X']

@pytest.fixture()
def ordered_activities_mapping():
    ordered_activities_mapping = {'Commodities':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'OthPart_IOT':['Labour_Tax', 'Labour_income'],
                                  'Sectors':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'FC':['I', 'X'],
                                  'EnerSect':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'Value_Added':['Labour_Tax', 'Labour_income'],
                                  'NonSupplierSect':['Coking_coal', 'Crude_oil', 'Natural_gas']}
    return ordered_activities_mapping

def test_change_activities_order_in(activities_mapping_part, IOT_part_headers, 
                                    ordered_activities_mapping):
    reordered_activities_mapping = data_mgmt._change_activities_order_in(activities_mapping_part, 
                                                                         IOT_part_headers)
    assert reordered_activities_mapping == ordered_activities_mapping

@pytest.fixture()
def activities_coordinates_mapping():
    activities_coordinates_mapping = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                            ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                      'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                            ['I', 'X']],
                                      'OthPart_IOT':[['Labour_Tax', 'Labour_income'],
                                                     ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    return activities_coordinates_mapping
    
def test_map_categories_to_activities_coordinates(categories_coordinates, 
                                                  ordered_activities_mapping, 
                                                  activities_coordinates_mapping):
    mapped_activities_coordinates_mapping = data_mgmt.map_categories_to_activities_coordinates(categories_coordinates, 
                                                                                               ordered_activities_mapping)
    assert mapped_activities_coordinates_mapping == activities_coordinates_mapping

def test_extract_IOTs_from(part_IOT, activities_coordinates_mapping, capsys):
    extracted_IOTs = data_mgmt.extract_IOTs_from(part_IOT, 
                                                 activities_coordinates_mapping)
    assert ((len(extracted_IOTs) == 3) & (not capsys.readouterr().err))
    #FIXME test too weak, might not be able to distinguish which assertions fails

def test_disaggregate_in_coordinates_mapping(categories_coordinates, 
                                             ordered_activities_mapping, 
                                             activities_coordinates_mapping):
    activities_coordinates_with_activities = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                                    ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                                    ['I', 'X']],
                                              'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                                   ['I']],
                                              'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                                   ['X']],
                                              'OthPart_IOT':[['Labour_Tax', 'Labour_income'], 
                                                             ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'Labour_Tax':[['Labour_Tax'], 
                                                            ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'Labour_income':[['Labour_income'], 
                                                               ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    to_expand_categories = ['FC', 'OthPart_IOT']
    reference_category = 'IC'
    disaggregated_activities_coordinates_mapping = data_mgmt.disaggregate_in_coordinates_mapping(activities_coordinates_mapping,
                                                                                                 to_expand_categories,
                                                                                                 reference_category)
    assert disaggregated_activities_coordinates_mapping == activities_coordinates_with_activities

def test_disaggregate_coordinates(activities_coordinates_mapping):
    new_activities_coordinates_mapping = {'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                               ['I']],
                                          'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], 
                                               ['X']]}
    disaggregated_activities_coordinates_mapping = data_mgmt._disaggregate_coordinates(activities_coordinates_mapping['FC'], 
                                                                                       activities_coordinates_mapping['IC'])
    assert disaggregated_activities_coordinates_mapping == new_activities_coordinates_mapping

def test_get_dissimilar_coordinates_index(activities_coordinates_mapping):
    assert data_mgmt._get_dissimilar_coordinates_index(activities_coordinates_mapping['FC'], 
                                                       activities_coordinates_mapping['IC']) == 1

@pytest.fixture()
def balance_tolerance():
    return 1E-2

@pytest.fixture()
def use_categories():
    return ['IC', 'OthPart_IOT']

@pytest.fixture()
def ressource_categories():
    return ['IC', 'FC']

def test_check_use_ressource_warns_when_unbalanced(part_IOT, 
                                                   activities_coordinates_mapping,
                                                   use_categories,
                                                   ressource_categories,
                                                   balance_tolerance, capsys):
    data_mgmt.check_use_ressource(part_IOT, activities_coordinates_mapping,
                                  use_categories, ressource_categories, 
                                  balance_tolerance)
    captured = capsys.readouterr()
    assert captured.err == "Warning : unbalanced IOT"+linebreaker+\
                           "Crude_oil, Natural_gas"+linebreaker

def test_combine_category_coordinates(activities_coordinates_mapping, IOT_part_headers):
    expected_consolidated_activities = [['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
                                        ['Coking_coal', 'Crude_oil', 'Natural_gas']]
    consolidated_activities = data_mgmt._combine_category_coordinates(['IC', 'OthPart_IOT'], 
                                                                      activities_coordinates_mapping,
                                                                      IOT_part_headers)
    assert consolidated_activities == expected_consolidated_activities

activities_mapping_full_file_path = mock_data_dir+'ordered_activities_mapping.csv'

def test_check_use_ressource_balance(full_IOT, categories_coordinates,
                                     use_categories, ressource_categories,
                                     balance_tolerance, capsys):
    activities_mapping_full = data_mgmt.read_activities_mapping(activities_mapping_full_file_path, 
                                                                delimiter=';')
    activities_coordinates_mapping = data_mgmt.map_categories_to_activities_coordinates(categories_coordinates, 
                                                                                        activities_mapping_full)
    data_mgmt.check_use_ressource(full_IOT, activities_coordinates_mapping, 
                                  use_categories, ressource_categories,
                                  balance_tolerance)
    assert not capsys.readouterr().err