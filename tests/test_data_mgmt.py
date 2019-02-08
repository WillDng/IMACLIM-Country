# coding: utf-8

import pytest
import pandas
from code import data_mgmt
from code.data_mgmt import linebreaker, dir_separator

mock_data_dir = 'tests/mock_data/'
part_IOT_path = mock_data_dir+'IOT_part.csv'
full_IOT_path = mock_data_dir+'IOT_Val.csv'
IOT_delimiter = ';'

@pytest.fixture()
def part_IOT():
    return pandas.read_csv(part_IOT_path, 
                           delimiter=IOT_delimiter,
                           index_col=0)

@pytest.fixture()
def bad_delimiter_IOT():
    return pandas.read_csv(part_IOT_path)

@pytest.fixture()
def full_IOT():
    return pandas.read_csv(full_IOT_path, 
                           delimiter=IOT_delimiter,
                           index_col=0)

def test_import_IOT(part_IOT):
    read_IOT = data_mgmt.import_IOT(part_IOT_path, delimiter=';')
    assert read_IOT.equals(part_IOT)

def test_import_IOT_non_correct_column_header():
    read_IOT = data_mgmt.import_IOT(part_IOT_path)
    assert all([isinstance(header, str) for header in read_IOT.index])

def test_get_filename_from_path():
    filename = data_mgmt.get_filename_from(part_IOT_path)
    assert filename == part_IOT_path.split(dir_separator)[-1]

def test_import_bad_delimiter_IOT(capsys):
    data_mgmt.import_IOT(part_IOT_path)
    IOT_name = data_mgmt.get_filename_from(part_IOT_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : IOT delimiter might not be correctly informed in "+IOT_name+linebreaker

def test_get_IOT_header_from(part_IOT):
    header = data_mgmt.get_IOT_header_from(part_IOT)
    IOT_header = next(open(part_IOT_path)).rstrip(linebreaker).split(IOT_delimiter)[1:]
    assert header == IOT_header

IOT_aggregation_file_path = mock_data_dir+'IOT_aggregation_part.csv'

@pytest.fixture()
def IOT_aggregation_mock_part():
    return {'Commodities':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'OthPart_IOT':['Labour_income', 'Labour_Tax'],
            'Sectors':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'FC':['I', 'X'],
            'EnerSect':['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'Value_Added':['Labour_income', 'Labour_Tax'],
            'NonSupplierSect':['Crude_oil', 'Natural_gas', 'Coking_coal']}

def test_read_IOT_aggregation_from(IOT_aggregation_mock_part):
    IOT_aggregation = data_mgmt.read_IOT_aggregation_from(IOT_aggregation_file_path, 
                                                          delimiter=';')
    assert IOT_aggregation == IOT_aggregation_mock_part

def test_read_IOT_aggregation_raise_delimiter_warning(capsys):
    data_mgmt.read_IOT_aggregation_from(IOT_aggregation_file_path)
    captured = capsys.readouterr()
    assert captured.err == "Warning : delimiter might not be correctly informed in function"

#FIXME might need to inform type of slice e.g:IC
def test_slice_warning_when_bad_headers(full_IOT, part_IOT, capsys):
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
def ill_ordered_aggregates():
    return ['Natural_gas', 'Coking_coal', 'Crude_oil']

@pytest.fixture()
def correct_header():
    return ['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X']

@pytest.fixture()
def part_IOT_headers(part_IOT):
    return [part_IOT.columns.values, part_IOT.index.values]

def test_get_correct_header(part_IOT_headers, ill_ordered_aggregates, correct_header):
    assert data_mgmt._get_correct_header(ill_ordered_aggregates, part_IOT_headers) == correct_header

def test_change_order_of(ill_ordered_aggregates, correct_header):
    assert data_mgmt._change_order_of(ill_ordered_aggregates, correct_header) == ['Coking_coal', 'Crude_oil', 'Natural_gas']

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

def test_change_individuals_order_in(IOT_aggregation_mock_part, part_IOT_headers, expected_IOT_aggregation):
    data_mgmt._change_individuals_order_in(IOT_aggregation_mock_part, part_IOT_headers)
    assert IOT_aggregation_mock_part == expected_IOT_aggregation

def test_translate_grouping_to_individuals(expected_IOT_grouping, expected_IOT_aggregation):
    data_mgmt._translate_grouping_to_individuals(expected_IOT_grouping, expected_IOT_aggregation)
    expected_grouping = {'IC':[['Coking_coal', 'Crude_oil', 'Natural_gas'],['Coking_coal', 'Crude_oil', 'Natural_gas']],
                         'FC':[['Coking_coal', 'Crude_oil', 'Natural_gas'], ['I', 'X']],
                         'OthPart_IOT':[['Labour_Tax', 'Labour_income'], ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    assert expected_IOT_grouping == expected_grouping

# def test_extract_IOTs_from(part_IOT, expected_IOT_grouping):
#     breakpoint()
#     initial_value = data_mgmt.extract_IOTs_from(part_IOT, expected_IOT_grouping)