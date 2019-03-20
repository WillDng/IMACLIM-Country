# coding: utf-8

import sys
import pytest
import src.common_utils as cu
from src.parameters import linebreaker


def test_warns_if_bad_delimiter(capsys):
    file_content = [['Crude_oil;Commodities;EnerSect'],
                    ['Natural_gas;Commodities;EnerSect']]
    file_path = 'path/to/file.csv'
    cu._warns_if_bad_delimiter(file_content, file_path)
    callers_name = sys._getframe(2).f_code.co_name
    assert capsys.readouterr().err == "Warning : delimiter might not be correctly informed in " + \
                                      callers_name + "() for " + file_path + linebreaker


expected_duplicates = ['Crude_oil', 'Natural_gas', 'Coking_coal', 'Bituminous_coal']


def test_remove_trailing_blanks():
    file_content = [['Crude_oil', 'Commodities', 'EnerSect', '', ''],
                    ['Natural_gas', 'Commodities', 'EnerSect', ''],
                    ['Coking_coal', 'Commodities', 'EnerSect', '', '', '']]
    expected_file_content = [['Crude_oil', 'Commodities', 'EnerSect'],
                             ['Natural_gas', 'Commodities', 'EnerSect'],
                             ['Coking_coal', 'Commodities', 'EnerSect']]
    assert cu._remove_trailing_blanks(file_content) == expected_file_content


def test_filter_list_duplicate():
    index_input = iter([['Crude_oil','Commodities'],
                        ['Natural_gas','Commodities'],
                        ['Coking_coal','Commodities'],
                        ['Bituminous_coal','Commodities'],
                        ['Crude_oil','-'],
                        ['Natural_gas','-'],
                        ['Coking_coal','-'],
                        ['Bituminous_coal','-']])
    expected_index = iter([['Crude_oil','Commodities'],
                           ['Natural_gas','Commodities'],
                           ['Coking_coal','Commodities'],
                           ['Bituminous_coal','Commodities']])
    filtered_data, duplicates = cu.filter_list_duplicate(index_input, 'path_to_file')
    assert ((list(filtered_data) == list(expected_index)) and (duplicates == expected_duplicates))


def test_filter_list_duplicate_raises():
    with pytest.raises(cu.InputError, match=r'Crude_oil, Natural_gas, Coking_coal, Bituminous_coal ' \
                                              'have duplicates in path_to_file'):
        _, _ = cu.raise_if_duplicates(expected_duplicates, 'path_to_file')
