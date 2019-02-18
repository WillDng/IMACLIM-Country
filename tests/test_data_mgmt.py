# coding: utf-8

import numpy as np
import pytest
import pandas as pd
from code import data_mgmt
from code.data_mgmt import linebreaker

mock_data_dir = 'tests/mock_data/'
part_IOT_path = mock_data_dir+'IOT_part.csv'
full_IOT_path = mock_data_dir+'IOT_Val.csv'
IOT_delimiter = ';'

@pytest.fixture()
def part_IOT():
    IOT_header = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X']
    IOT_col_header = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income']
    IOT_data = np.array([[0, 0, 0, 0, 19609.61370695],
                         [0, 0, 0, 0, 24190.37317909],
                         [0, 3225.19564403, 0, 0, 513333.19103917],
                         [0, 9044.45950877, 556606.98333951, 0, 0], 
                         [0, 20587.91760946, 1267005.36419441, 0, 0]])
    return pd.DataFrame(IOT_data, index=IOT_col_header, columns=IOT_header)

@pytest.fixture()
def full_IOT():
    return pd.read_csv(full_IOT_path, 
                           delimiter=IOT_delimiter,
                           index_col=0)

def test_import_bad_delimiter_IOT(capsys):
    data_mgmt.read_IOT(part_IOT_path)
    IOT_name = data_mgmt.get_filename_from(part_IOT_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : IOT delimiter might not be correctly informed in "+IOT_name+linebreaker

IOT_aggregation_part_file_path = mock_data_dir+'IOT_aggregation_part.csv'

@pytest.fixture()
def IOT_aggregation_part():
    return {'Commodities':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'OthPart_IOT':['Labour_income', 'Labour_Tax'],
            'Sectors':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'FC':['I', 'X'],
            'EnerSect':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'Value_Added':['Labour_income', 'Labour_Tax'],
            'NonSupplierSect':['Crude_oil', 'Natural_gas', 'Coking_coal']}

def test_read_IOT_aggregation_from(IOT_aggregation_part):
    IOT_aggregation = data_mgmt.read_IOT_aggregation_from(IOT_aggregation_part_file_path, 
                                                          delimiter=';')
    assert IOT_aggregation == IOT_aggregation_part

def test_read_IOT_aggregation_raise_delimiter_warning(capsys):
    data_mgmt.read_IOT_aggregation_from(IOT_aggregation_part_file_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : delimiter might not be correctly informed in read_IOT_aggregation_from()"+linebreaker

#FIXME might need to inform type of slice e.g:IC
def test_slice_warning_when_bad_headers(full_IOT, capsys):
    wrong_headers = (['Coking_coal', 'I'], ['Natural_gas', 'Labour_Tax'])
    data_mgmt._slice_(full_IOT, wrong_headers)
    captured = capsys.readouterr()
    assert captured.err == "Warning : IOT headers might be ill informed"+linebreaker

@pytest.fixture()
def expected_IOT_grouping():
    expected_IOT_grouping = {'IC':['Commodities','Sectors'],
                             'FC':['Commodities', 'FC'],
                             'OthPart_IOT':['OthPart_IOT', 'Sectors']}
    return expected_IOT_grouping

def test_read_grouping_from(expected_IOT_grouping):
    grouping_file_path = mock_data_dir + 'IOT_grouping.csv'
    read_grouping = data_mgmt.read_grouping_from(grouping_file_path)
    assert read_grouping == expected_IOT_grouping

@pytest.fixture()
def ill_ordered_individuals():
    return ['Natural_gas', 'Coking_coal', 'X', 'Crude_oil']

@pytest.fixture()
def part_IOT_headers():
    return [pd.Index(['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
            dtype='object', name='Values'),
            pd.Index(['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X'], 
            dtype='object')]

def test_get_correct_header(ill_ordered_individuals, part_IOT_headers):
    assert data_mgmt._get_correct_header(ill_ordered_individuals, part_IOT_headers).equals(part_IOT_headers[1])

def test_change_order_of(ill_ordered_individuals, part_IOT_headers):
    assert data_mgmt._change_order_of(ill_ordered_individuals, part_IOT_headers[1]) == ['Coking_coal', 'Crude_oil', 'Natural_gas', 'X']

@pytest.fixture()
def expected_IOT_aggregation():
    expected_IOT_aggregation = {'Commodities':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                'OthPart_IOT':['Labour_Tax', 'Labour_income'],
                                'Sectors':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                'FC':['I', 'X'],
                                'EnerSect':['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                'Value_Added':['Labour_Tax', 'Labour_income'],
                                'NonSupplierSect':['Coking_coal', 'Crude_oil', 'Natural_gas']}
    return expected_IOT_aggregation

def test_change_individuals_order_in(IOT_aggregation_part, part_IOT_headers, expected_IOT_aggregation):
    data_mgmt._change_individuals_order_in(IOT_aggregation_part, part_IOT_headers)
    assert IOT_aggregation_part == expected_IOT_aggregation

@pytest.fixture()
def expected_expanded_grouping():
    expected_expanded_grouping = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                  'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I', 'X']],
                                  'OthPart_IOT':[['Labour_Tax', 'Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    return expected_expanded_grouping
    
def test_translate_grouping_to_individuals(expected_IOT_grouping, expected_IOT_aggregation, expected_expanded_grouping):
    expanded_grouping = data_mgmt.translate_grouping_to_individuals(expected_IOT_grouping, expected_IOT_aggregation)
    assert expanded_grouping == expected_expanded_grouping

def test_extract_IOTs_from(part_IOT, expected_expanded_grouping, capsys):
    initial_value = data_mgmt.extract_IOTs_from(part_IOT, expected_expanded_grouping)
    assert ((len(initial_value) == 3) & (not capsys.readouterr().err))
    #FIXME test too weak, might not be able to distinguish which assertions fails

def test_add_individuals_in_expanded_grouping(expected_IOT_grouping, expected_IOT_aggregation, expected_expanded_grouping):
    expected_expanded_grouping_with_individuals = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                                   'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I', 'X']],
                                                   'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I']],
                                                   'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['X']],
                                                   'OthPart_IOT':[['Labour_Tax', 'Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                                   'Labour_Tax':[['Labour_Tax'], ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                                   'Labour_income':[['Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    data_mgmt.add_individuals_in_expanded_grouping(expected_expanded_grouping)
    assert expected_expanded_grouping == expected_expanded_grouping_with_individuals

def test_generate_individuals_in_expanded_grouping(expected_expanded_grouping):
    expected_expanded_individuals_grouping = {'I':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I']],
                                              'X':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['X']]}
    generated_expanded_individuals_grouping = data_mgmt._generate_individuals_in_expanded_grouping(expected_expanded_grouping['FC'], expected_expanded_grouping['IC'])
    assert generated_expanded_individuals_grouping == expected_expanded_individuals_grouping

def test_get_different_list_index(expected_expanded_grouping):
    assert data_mgmt._get_different_list_index(expected_expanded_grouping['FC'], expected_expanded_grouping['IC']) == 1

def test_check_use_ressource_warning_when_unbalanced(part_IOT, expected_expanded_grouping, capsys):
    use_headers = ['IC', 'OthPart_IOT']
    ressources_headers = ['IC', 'FC']
    data_mgmt.check_use_ressource(part_IOT, expected_expanded_grouping, use_headers, ressources_headers)
    captured = capsys.readouterr()
    assert captured.err == "Warning : unbalanced IOT"+linebreaker+"Crude_oil, Natural_gas"+linebreaker

def test_consolidate_headers(expected_expanded_grouping, part_IOT_headers):
    expected_consolidated_headers = [['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
                                     ['Coking_coal', 'Crude_oil', 'Natural_gas']]
    consolidated_headers = data_mgmt._consolidate_headers(['IC', 'OthPart_IOT'], expected_expanded_grouping, part_IOT_headers)
    assert consolidated_headers == expected_consolidated_headers

IOT_aggregation_full_file_path = mock_data_dir+'IOT_aggregation.csv'

def test_check_use_ressource_balance(full_IOT, expected_IOT_grouping, capsys):
    IOT_full_aggregation = data_mgmt.read_IOT_aggregation_from(IOT_aggregation_full_file_path, delimiter=';')
    expanded_grouping = data_mgmt.translate_grouping_to_individuals(expected_IOT_grouping, IOT_full_aggregation)
    ressources = ['IC', 'FC']
    uses = ['IC', 'OthPart_IOT']
    data_mgmt.check_use_ressource(full_IOT, expanded_grouping, uses, ressources)
    assert not capsys.readouterr().err
