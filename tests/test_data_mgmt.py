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
    assert captured.err == "Warning : IOT delimiter might not be correctly informed in "+data_mgmt.get_filename_from(part_IOT_path)+linebreaker

@pytest.fixture()
def activities_category_mapping_part():
    return {'Commodities':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'OthPart_IOT':['Labour_income', 'Labour_Tax'],
            'Sectors':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'FC':['I', 'X'],
            'EnerSect':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'Value_Added':['Labour_income', 'Labour_Tax'],
            'NonSupplierSect':['Crude_oil', 'Natural_gas', 'Coking_coal']}

IOT_activities_category_mapping_part_file_path = mock_data_dir+'activities_category_mapping_part.csv'

def test_read_activities_category_mapping(activities_category_mapping_part):
    read_activities_mapping = data_mgmt.read_activities_category_mapping(IOT_activities_category_mapping_part_file_path, 
                                                          delimiter=';')
    assert read_activities_mapping == activities_category_mapping_part

def test_read_activities_category_mapping_warns_when_bad_delimiter(capsys):
    data_mgmt.read_activities_category_mapping(IOT_activities_category_mapping_part_file_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : delimiter might not be correctly informed in read_activities_category_mapping() for "+data_mgmt.get_filename_from(IOT_activities_category_mapping_part_file_path)+linebreaker

full_IOT_path = mock_data_dir+'IOT_Val.csv'

@pytest.fixture()
def full_IOT():
    return pd.read_csv(full_IOT_path, 
                           delimiter=IOT_delimiter,
                           index_col=0)

#FIXME might need to inform type of slice e.g:IC
def test_slice_warns_when_bad_activities_coordinates(full_IOT, capsys):
    bad_activities_coordinates = (['Coking_coal', 'I'], ['Natural_gas', 'Labour_Tax'])
    data_mgmt._slice(full_IOT, bad_activities_coordinates)
    captured = capsys.readouterr()
    assert captured.err == "Warning : IOT activities coordinates might be ill informed"+linebreaker

@pytest.fixture()
def category_coordinates():
    category_coordinates = {'IC':['Commodities','Sectors'],
                            'FC':['Commodities', 'FC'],
                            'OthPart_IOT':['OthPart_IOT', 'Sectors']}
    return category_coordinates

def test_read_category_coordinates_from(category_coordinates):
    category_coordinates_filepath = mock_data_dir + 'category_coordinates.csv'
    read_category_coordinates = data_mgmt.read_category_coordinates_from(category_coordinates_filepath)
    assert read_category_coordinates == category_coordinates

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
    assert data_mgmt._change_order_of(ill_ordered_activities, IOT_part_headers[1]) == ['Coking_coal', 'Crude_oil', 'Natural_gas', 'X']

@pytest.fixture()
def ordered_activities_category_mapping():
    ordered_activities_category_mapping = {'Commodities':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                           'OthPart_IOT':['Labour_Tax', 'Labour_income'],
                                           'Sectors':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                           'FC':['I', 'X'],
                                           'EnerSect':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                           'Value_Added':['Labour_Tax', 'Labour_income'],
                                           'NonSupplierSect':['Coking_coal', 'Crude_oil', 'Natural_gas']}
    return ordered_activities_category_mapping

def test_change_activities_order_in(activities_category_mapping_part, IOT_part_headers, ordered_activities_category_mapping):
    reordered_activities_category_mapping = data_mgmt._change_activities_order_in(activities_category_mapping_part, IOT_part_headers)
    assert reordered_activities_category_mapping == ordered_activities_category_mapping

@pytest.fixture()
def activities_coordinates_category_mapping():
    activities_coordinates_category_mapping = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                               'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I', 'X']],
                                               'OthPart_IOT':[['Labour_Tax', 'Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    return activities_coordinates_category_mapping
    
def test_map_category_to_activities(category_coordinates, ordered_activities_category_mapping, activities_coordinates_category_mapping):
    mapped_activities_coordinates_category_mapping = data_mgmt.map_category_to_activities(category_coordinates, ordered_activities_category_mapping)
    assert mapped_activities_coordinates_category_mapping == activities_coordinates_category_mapping

def test_extract_IOTs_from(part_IOT, activities_coordinates_category_mapping, capsys):
    extracted_IOTs = data_mgmt.extract_IOTs_from(part_IOT, activities_coordinates_category_mapping)
    assert ((len(extracted_IOTs) == 3) & (not capsys.readouterr().err))
    #FIXME test too weak, might not be able to distinguish which assertions fails

def test_disaggregate_in_coordinates_category_mapping(category_coordinates, ordered_activities_category_mapping, activities_coordinates_category_mapping):
    activities_coordinates_with_activities = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I', 'X']],
                                              'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I']],
                                              'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['X']],
                                              'OthPart_IOT':[['Labour_Tax', 'Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'Labour_Tax':[['Labour_Tax'], ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                              'Labour_income':[['Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    disaggregated_activities_coordinates_category_mapping = data_mgmt.disaggregate_in_coordinates_category_mapping(activities_coordinates_category_mapping)
    assert disaggregated_activities_coordinates_category_mapping == activities_coordinates_with_activities

def test_disaggregate_coordinates(activities_coordinates_category_mapping):
    new_activities_coordinates_category_mapping = {'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I']],
                                                   'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['X']]}
    disaggregated_activities_coordinates_category_mapping = data_mgmt._disaggregate_coordinates(activities_coordinates_category_mapping['FC'], 
                                                                                                activities_coordinates_category_mapping['IC'])
    assert disaggregated_activities_coordinates_category_mapping == new_activities_coordinates_category_mapping

def test_get_dissimilar_coordinates_index(activities_coordinates_category_mapping):
    assert data_mgmt._get_dissimilar_coordinates_index(activities_coordinates_category_mapping['FC'], activities_coordinates_category_mapping['IC']) == 1

def test_check_use_ressource_warns_when_unbalanced(part_IOT, activities_coordinates_category_mapping, capsys):
    use_headers = ['IC', 'OthPart_IOT']
    ressources_headers = ['IC', 'FC']
    data_mgmt.check_use_ressource(part_IOT, activities_coordinates_category_mapping, use_headers, ressources_headers)
    captured = capsys.readouterr()
    assert captured.err == "Warning : unbalanced IOT"+linebreaker+"Crude_oil, Natural_gas"+linebreaker

def test_combine_category_coordinates(activities_coordinates_category_mapping, IOT_part_headers):
    expected_consolidated_activities = [['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
                                        ['Coking_coal', 'Crude_oil', 'Natural_gas']]
    consolidated_activities = data_mgmt._combine_category_coordinates(['IC', 'OthPart_IOT'], 
                                                                      activities_coordinates_category_mapping,
                                                                      IOT_part_headers)
    assert consolidated_activities == expected_consolidated_activities

IOT_activities_mapping_full_file_path = mock_data_dir+'ordered_activities_category_mapping.csv'

def test_check_use_ressource_balance(full_IOT, category_coordinates, capsys):
    IOT_full_activities_mapping = data_mgmt.read_activities_category_mapping(IOT_activities_mapping_full_file_path, delimiter=';')
    expanded_grouping = data_mgmt.map_category_to_activities(category_coordinates, IOT_full_activities_mapping)
    ressources = ['IC', 'FC']
    uses = ['IC', 'OthPart_IOT']
    data_mgmt.check_use_ressource(full_IOT, expanded_grouping, uses, ressources)
    assert not capsys.readouterr().err
