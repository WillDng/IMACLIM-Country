# coding: utf-8

import sys
import pytest
from src import common_utils as cu
from src.parameters import linebreaker
from tests.test_Loading_data_lib import activities_mapping_part


def test_warns_if_bad_delimiter(capsys):
    file_content = [['Crude_oil;Commodities;EnerSect'],
                    ['Natural_gas;Commodities;EnerSect']]
    file_path = 'path/to/file.csv'
    cu._warns_if_bad_delimiter(file_content, file_path)
    callers_name = sys._getframe(2).f_code.co_name
    assert capsys.readouterr().err == "Warning : delimiter might not be correctly informed in " + \
                                      callers_name + "() for " + file_path + linebreaker


def test_remove_trailing_blanks():
    file_content = [['Crude_oil', 'Commodities', 'EnerSect', '', ''],
                    ['', 'Commodities', 'EnerSect', ''],
                    ['Coking_coal', 'Commodities', 'EnerSect', '', '', '']]
    expected_file_content = [['Crude_oil', 'Commodities', 'EnerSect'],
                             ['', 'Commodities', 'EnerSect'],
                             ['Coking_coal', 'Commodities', 'EnerSect']]
    assert cu._remove_trailing_blanks(file_content) == expected_file_content


expected_duplicates = ['Crude_oil', 'Natural_gas', 'Coking_coal', 'Bituminous_coal']


def test_filter_list_duplicate():
    index_input = iter([['Crude_oil', 'Commodities'],
                        ['Natural_gas', 'Commodities'],
                        ['Coking_coal', 'Commodities'],
                        ['Bituminous_coal', 'Commodities'],
                        ['Crude_oil', '-'],
                        ['Natural_gas', '-'],
                        ['Coking_coal', '-'],
                        ['Bituminous_coal', '-']])
    expected_index = iter([['Crude_oil', 'Commodities'],
                           ['Natural_gas', 'Commodities'],
                           ['Coking_coal', 'Commodities'],
                           ['Bituminous_coal', 'Commodities']])
    filtered_data, duplicates = cu.filter_list_duplicate(index_input)
    assert ((list(filtered_data) == list(expected_index)) and (duplicates == expected_duplicates))


def test_filter_list_duplicate_raises():
    with pytest.raises(cu.InputError, match=r'Crude_oil, Natural_gas, Coking_coal, Bituminous_coal ' \
                                              'have duplicates in path_to_file'):
        _, _ = cu.raise_if_duplicates(expected_duplicates, 'path_to_file')


activities_mapping = [['Crude_oil', 'Commodities', 'EnerSect'],
                      ['Natural_gas', 'Commodities', 'EnerSect'],
                      ['Coking_coal', 'Commodities', 'EnerSect'],
                      ['Labour_income', 'OthPart_IOT', 'Value_Added'],
                      ['Labour_Tax', 'OthPart_IOT', 'Value_Added'],
                      ['Crude_oil', 'Sectors', 'NonSupplierSect'],
                      ['Natural_gas', 'Sectors', 'NonSupplierSect'],
                      ['Coking_coal', 'Sectors', 'NonSupplierSect'],
                      ['I', 'FC'],
                      ['X', 'FC']]


def test_extract_aggregation_mapping(activities_mapping_part):
    assert cu.extract_aggregation_mapping(activities_mapping) == activities_mapping_part


def test_partial_extract_aggregation_mapping():
    expected_partial_mapping = {'Commodities': ['Crude_oil', 'Natural_gas', 'Coking_coal'],
                                'OthPart_IOT': ['Labour_income', 'Labour_Tax'],
                                'Sectors': ['Crude_oil', 'Natural_gas', 'Coking_coal'],
                                'FC': ['I', 'X']}
    assert cu.extract_aggregation_mapping(activities_mapping,
                                          col=1) == expected_partial_mapping
