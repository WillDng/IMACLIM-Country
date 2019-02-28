# coding: utf-8

import numpy as np
import pytest
import pandas as pd
from src import data_mgmt
from src.parameters import linebreaker
import sys

mock_data_dir = 'tests/mock_data/'
IOT_delimiter = ';'


@pytest.fixture()
def part_IOT():
    IOT_uses = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X']
    IOT_ressources = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income']
    IOT_data = np.array([[0.,       0.      ,        0.       , 0., 19609.61370695 ],
                         [0.,       0.      ,        0.       , 0., 24190.37317909 ],
                         [0., 3225.19564403 ,        0.       , 0., 513333.19103917],
                         [0., 9044.45950877 , 556606.98333951 , 0.,        0.      ],
                         [0., 20587.91760946, 1267005.36419441, 0.,        0.      ]])
    return pd.DataFrame(IOT_data, index=IOT_ressources, columns=IOT_uses)


@pytest.fixture()
def activities_mapping_part():
    return {'Commodities': ['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'OthPart_IOT': ['Labour_income', 'Labour_Tax'],
            'Sectors': ['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'FC': ['I', 'X'],
            'EnerSect': ['Crude_oil', 'Natural_gas', 'Coking_coal'],
            'Value_Added': ['Labour_income', 'Labour_Tax'],
            'NonSupplierSect': ['Crude_oil', 'Natural_gas', 'Coking_coal']}


# def test_read_activities_mapping(activities_mapping_part):
#     read_activities_mapping = data_mgmt.read_activities_mapping(activities_mapping_part_file_path,
#                                                                 delimiter=';')
#     assert read_activities_mapping == activities_mapping_part
#

def test_parse_activities_mapping(activities_mapping_part):
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
    assert data_mgmt._aggregate_activities(activities_mapping) == activities_mapping_part


def test_warns_if_bad_delimiter(capsys):
    file_content = [['Crude_oil;Commodities;EnerSect'],
                    ['Natural_gas;Commodities;EnerSect']]
    file_path = 'path/to/file.csv'
    data_mgmt._warns_if_bad_delimiter(file_content, file_path)
    callers_name = sys._getframe(2).f_code.co_name
    assert capsys.readouterr().err == "Warning : delimiter might not be correctly informed in " + \
                                      callers_name + "() for file.csv" + linebreaker


full_IOT_path = mock_data_dir + 'IOT_Val.csv'


@pytest.fixture()
def full_IOT():
    return pd.read_csv(full_IOT_path,
                       delimiter=IOT_delimiter,
                       index_col=0)


def test_slice_activities(part_IOT):
    index = ['Natural_gas', 'Labour_Tax']
    columns = ['Crude_oil', 'Natural_gas']
    coordinates = [index, columns]
    expected_sliced_IOT = pd.DataFrame(np.array([[  3225.19564403,      0.        ],
                                                 [  9044.45950877, 556606.98333951]]),
                                       index=index,
                                       columns=columns)
    pd.testing.assert_frame_equal(data_mgmt._slice_activities(part_IOT, coordinates), expected_sliced_IOT)


def test_check_coordinates_in_IOT(part_IOT, capsys):
    bad_coordinates = [['Crude_oil', 'Natural_gas'], ['Natural_gas', 'Labour_Tax']]
    data_mgmt._check_coordinates_in_IOT(part_IOT, bad_coordinates)
    assert capsys.readouterr().err == "Warning : wrong coordinates" + linebreaker + \
                                      "Labour_Tax not in columns" + linebreaker


@pytest.fixture()
def categories_coordinates_mapping():
    categories_coordinates_mapping = {'IC': ['Commodities', 'Sectors'],
                                      'FC': ['Commodities', 'FC'],
                                      'OthPart_IOT': ['OthPart_IOT', 'Sectors']}
    return categories_coordinates_mapping

# categories_coordinates_mapping_filepath = mock_data_dir + 'categories_coordinates_mapping.csv'

# def test_read_categories_coordinates_mapping(categories_coordinates_mapping):
#     assert data_mgmt.read_categories_coordinates_mapping(categories_coordinates_mapping_filepath) == categories_coordinates_mapping


def test_map_categories_to_coordinates(categories_coordinates_mapping):
    categories_coordinates_mapping_data = [['IC', 'Commodities', 'Sectors'],
                                           ['FC', 'Commodities', 'FC'],
                                           ['OthPart_IOT', 'OthPart_IOT', 'Sectors']]
    assert data_mgmt._map_categories_to_coordinates(categories_coordinates_mapping_data) == categories_coordinates_mapping


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
    pd.testing.assert_index_equal(data_mgmt._get_matching_header_for(ill_ordered_activities, IOT_part_headers), IOT_part_headers[1])


def test_change_order_of(ill_ordered_activities, IOT_part_headers):
    assert data_mgmt._change_order_of(ill_ordered_activities,
                                      IOT_part_headers[1]) == ['Coking_coal', 'Crude_oil', 'Natural_gas', 'X']


@pytest.fixture()
def ordered_activities_mapping():
    ordered_activities_mapping = {'Commodities': ['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'OthPart_IOT': ['Labour_Tax', 'Labour_income'],
                                  'Sectors': ['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'FC': ['I', 'X'],
                                  'EnerSect': ['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                  'Value_Added': ['Labour_Tax', 'Labour_income'],
                                  'NonSupplierSect': ['Coking_coal', 'Crude_oil', 'Natural_gas']}
    return ordered_activities_mapping


def test_change_activities_order_in(activities_mapping_part, IOT_part_headers,
                                    ordered_activities_mapping):
    reordered_activities_mapping = data_mgmt._change_activities_order_in(activities_mapping_part,
                                                                         IOT_part_headers)
    assert reordered_activities_mapping == ordered_activities_mapping


@pytest.fixture()
def activities_coordinates_mapping():
    activities_coordinates_mapping = {'IC': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                             ['Coking_coal', 'Crude_oil', 'Natural_gas']],
                                      'FC': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                             ['I', 'X']],
                                      'OthPart_IOT': [['Labour_Tax', 'Labour_income'],
                                                      ['Coking_coal', 'Crude_oil', 'Natural_gas']]}
    return activities_coordinates_mapping


def test_map_categories_to_activities_coordinates(categories_coordinates_mapping,
                                                  ordered_activities_mapping,
                                                  activities_coordinates_mapping):
    mapped_activities_coordinates_mapping = data_mgmt.map_categories_to_activities_coordinates(categories_coordinates_mapping,
                                                                                               ordered_activities_mapping)
    assert mapped_activities_coordinates_mapping == activities_coordinates_mapping


def test_extract_IOTs_from(part_IOT, activities_coordinates_mapping, capsys):
    extracted_IOTs = data_mgmt.extract_IOTs_from(part_IOT,
                                                 activities_coordinates_mapping)
    assert ((len(extracted_IOTs) == 3) & (not capsys.readouterr().err))
    # FIXME test too weak, might not be able to distinguish which assertions fails


@pytest.fixture()
def activities_coordinates_with_activities():
    return {'IC': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                   ['Coking_coal', 'Crude_oil', 'Natural_gas']],
            'FC': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                   ['I', 'X']],
            'I': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                  ['I']],
            'X': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                  ['X']],
            'OthPart_IOT': [['Labour_Tax', 'Labour_income'],
                            ['Coking_coal', 'Crude_oil', 'Natural_gas']],
            'Labour_Tax': [['Labour_Tax'],
                           ['Coking_coal', 'Crude_oil', 'Natural_gas']],
            'Labour_income': [['Labour_income'],
                              ['Coking_coal', 'Crude_oil', 'Natural_gas']]}


def test_disaggregate_in_coordinates_mapping(categories_coordinates_mapping,
                                             ordered_activities_mapping,
                                             activities_coordinates_mapping,
                                             activities_coordinates_with_activities):
    to_expand_categories = ['FC', 'OthPart_IOT']
    reference_category = 'IC'
    disaggregated_activities_coordinates_mapping = data_mgmt.disaggregate_in_coordinates_mapping(activities_coordinates_mapping,
                                                                                                 to_expand_categories,
                                                                                                 reference_category)
    assert disaggregated_activities_coordinates_mapping == activities_coordinates_with_activities


def test_disaggregate_coordinates(activities_coordinates_mapping):
    new_activities_coordinates_mapping = {'I': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                                ['I']],
                                          'X': [['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                                ['X']]}
    disaggregated_activities_coordinates_mapping = data_mgmt._disaggregate_coordinates(activities_coordinates_mapping['FC'],
                                                                                       activities_coordinates_mapping['IC'])
    assert disaggregated_activities_coordinates_mapping == new_activities_coordinates_mapping


def test_get_dissimilar_coordinates_index(activities_coordinates_mapping):
    assert data_mgmt._get_dissimilar_coordinates_index(activities_coordinates_mapping['FC'],
                                                       activities_coordinates_mapping['IC']) == 1


# @pytest.fixture()
# def use_categories():
#     return ['IC', 'OthPart_IOT']


# @pytest.fixture()
# def ressource_categories():
#     return ['IC', 'FC']

# def test_check_use_ressource_warns_when_unbalanced(part_IOT,
#                                                    activities_coordinates_mapping,
#                                                    use_categories,
#                                                    ressource_categories,
#                                                    balance_tolerance, capsys):
#     data_mgmt.check_use_ressource(part_IOT, activities_coordinates_mapping,
#                                   use_categories, ressource_categories,
#                                   balance_tolerance)
#     captured = capsys.readouterr()
#     assert captured.err == "Warning : unbalanced IOT"+linebreaker+\
#                            "Crude_oil, Natural_gas"+linebreaker


# def test_combine_category_coordinates(activities_coordinates_mapping, IOT_part_headers):
#     expected_consolidated_activities = [['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income'],
#                                         ['Coking_coal', 'Crude_oil', 'Natural_gas']]
#     consolidated_activities = data_mgmt._combine_category_coordinates(['IC', 'OthPart_IOT'],
#                                                                       activities_coordinates_mapping,
#                                                                       IOT_part_headers)
#     assert list(consolidated_activities) == expected_consolidated_activities


# activities_mapping_full_file_path = mock_data_dir + 'ordered_activities_mapping.csv'

# def test_check_use_ressource_balance(full_IOT, categories_coordinates_mapping,
#                                      use_categories, ressource_categories,
#                                      balance_tolerance, capsys):
#     activities_mapping_full = data_mgmt.read_activities_mapping(activities_mapping_full_file_path,
#                                                                 delimiter=';')
#     activities_coordinates_mapping = data_mgmt.map_categories_to_activities_coordinates(categories_coordinates_mapping,
#                                                                                         activities_mapping_full)
#     data_mgmt.check_use_ressource(full_IOT, activities_coordinates_mapping,
#                                   use_categories, ressource_categories,
#                                   balance_tolerance)
#     assert not capsys.readouterr().err


def test_slice_and_sum(part_IOT):
    index = ['Natural_gas', 'Labour_Tax']
    columns = ['Crude_oil', 'Natural_gas']
    coordinates = [index, columns]
    expected_sum = pd.Series(np.array([3225.19564403, 565651.44284828]),
                             index=index)
    pd.testing.assert_series_equal(data_mgmt.slice_and_sum(part_IOT, coordinates, axis=1),
                                   expected_sum)


def test_get_ERE(full_IOT, activities_coordinates_with_activities):
    expected_ERE = pd.Series(np.array([19609.61370695, 11920.71802629, -40048.59665631]),
                             index=['Coking_coal', 'Crude_oil', 'Natural_gas'])
    use_categories = ['IC', 'Labour_Tax']
    ressource_categories = ['IC', 'FC']
    pd.testing.assert_series_equal(data_mgmt.get_ERE(use_categories, ressource_categories,
                                                     full_IOT, activities_coordinates_with_activities),
                                   expected_ERE,
                                   check_names=False)


def test_ERE_not_balanced(full_IOT, capsys):
    unbalanced_ERE = pd.Series(np.array([0.5, 0., -40048.59665631]),
                               index=['Coking_coal', 'Crude_oil', 'Natural_gas'])
    data_mgmt.is_ERE_balanced(unbalanced_ERE)
    assert capsys.readouterr().err == "Warning : unbalanced IOT" + linebreaker + \
                                      "Coking_coal, Natural_gas" + linebreaker
