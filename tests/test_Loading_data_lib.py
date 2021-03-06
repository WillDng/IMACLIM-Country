# coding: utf-8

import numpy as np
import pytest
import pandas as pd
from src import Loading_data_lib as ld
from src.parameters import linebreaker
from typing import (Any, Dict)

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


new_format_dir = 'new_format/data/FRA_update/'
full_IOT_path = new_format_dir + 'IOT_Val.csv'


@pytest.fixture()
def full_IOT():
    return pd.read_csv(full_IOT_path,
                       delimiter=IOT_delimiter,
                       index_col=0)


def test_slice_activities(part_IOT):
    index = ['Natural_gas', 'Labour_Tax']
    columns = ['Crude_oil', 'Natural_gas']
    coordinates = (index, columns)
    expected_sliced_IOT = pd.DataFrame(np.array([[  3225.19564403,      0.        ],
                                                 [  9044.45950877, 556606.98333951]]),
                                       index=index,
                                       columns=columns)
    pd.testing.assert_frame_equal(ld._slice_activities(part_IOT, coordinates), expected_sliced_IOT)


def test_check_coordinates_in_IOT(part_IOT, capsys):
    bad_coordinates = [['Crude_oil', 'Natural_gas'], ['Natural_gas', 'Labour_Tax']]
    ld._check_coordinates_in_IOT(part_IOT, bad_coordinates)
    assert capsys.readouterr().err == "Warning : wrong coordinates" + linebreaker + \
                                      "Labour_Tax not in columns" + linebreaker


@pytest.fixture()
def categories_coordinates_mapping():
    categories_coordinates_mapping = {'IC': ['Commodities', 'Sectors'],
                                      'FC': ['Commodities', 'FC'],
                                      'OthPart_IOT': ['OthPart_IOT', 'Sectors']}
    return categories_coordinates_mapping


def test_map_categories_to_coordinates(categories_coordinates_mapping):
    categories_coordinates_mapping_data = [['IC', 'Commodities', 'Sectors'],
                                           ['FC', 'Commodities', 'FC'],
                                           ['OthPart_IOT', 'OthPart_IOT', 'Sectors']]
    assert ld._map_categories_to_coordinates(categories_coordinates_mapping_data) == categories_coordinates_mapping


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
    pd.testing.assert_index_equal(ld.get_matching_header_for(ill_ordered_activities, IOT_part_headers), IOT_part_headers[1])


def test_change_order_of(ill_ordered_activities, IOT_part_headers):
    assert ld.change_order_of(ill_ordered_activities,
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
    reordered_activities_mapping = ld._change_activities_order_in(activities_mapping_part,
                                                                  IOT_part_headers)
    assert reordered_activities_mapping == ordered_activities_mapping


@pytest.fixture()
def activities_coordinates_mapping():
    activities_coordinates_mapping = {'IC': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                             ['Coking_coal', 'Crude_oil', 'Natural_gas']),
                                      'FC': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                             ['I', 'X']),
                                      'OthPart_IOT': (['Labour_Tax', 'Labour_income'],
                                                      ['Coking_coal', 'Crude_oil', 'Natural_gas'])}
    return activities_coordinates_mapping


def test_map_categories_to_activities_coordinates(categories_coordinates_mapping,
                                                  ordered_activities_mapping,
                                                  activities_coordinates_mapping):
    mapped_activities_coordinates_mapping = ld.map_categories_to_activities_coordinates(categories_coordinates_mapping,
                                                                                        ordered_activities_mapping)
    assert mapped_activities_coordinates_mapping == activities_coordinates_mapping


def test_warns_when_values_not_in_dict(activities_coordinates_mapping, capsys):
    interest_categories = ['IC', 'mock_header']
    ld._check_values_in_dict(interest_categories, activities_coordinates_mapping)
    assert capsys.readouterr().err == "Warning : mock_header not in mapping" + linebreaker


def test_extract_IOTs_from(part_IOT, activities_coordinates_mapping, capsys):
    extracted_IOTs = ld.extract_IOTs_from(part_IOT,
                                          activities_coordinates_mapping)
    assert ((len(extracted_IOTs) == 3) & (not capsys.readouterr().err))
    # FIXME test too weak, might not be able to distinguish which assertions fails


@pytest.fixture()
def activities_coordinates_with_activities():
    return {'IC': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                   ['Coking_coal', 'Crude_oil', 'Natural_gas']),
            'FC': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                   ['I', 'X']),
            'I': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                  ['I']),
            'X': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                  ['X']),
            'OthPart_IOT': (['Labour_Tax', 'Labour_income'],
                            ['Coking_coal', 'Crude_oil', 'Natural_gas']),
            'Labour_Tax': (['Labour_Tax'],
                           ['Coking_coal', 'Crude_oil', 'Natural_gas']),
            'Labour_income': (['Labour_income'],
                              ['Coking_coal', 'Crude_oil', 'Natural_gas'])}


def test_disaggregate_in_coordinates(categories_coordinates_mapping,
                                     ordered_activities_mapping,
                                     activities_coordinates_mapping,
                                     activities_coordinates_with_activities):
    to_expand_categories = ['FC', 'OthPart_IOT']
    reference_category = 'IC'
    disaggregated_activities_coordinates_mapping = ld.disaggregate_in_coordinates(activities_coordinates_mapping,
                                                                                  to_expand_categories,
                                                                                  reference_category)
    assert disaggregated_activities_coordinates_mapping == activities_coordinates_with_activities


def test_disaggregate_coordinates(activities_coordinates_mapping):
    new_activities_coordinates_mapping = {'I': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                                ['I']),
                                          'X': (['Coking_coal', 'Crude_oil', 'Natural_gas'],
                                                ['X'])}
    disaggregated_activities_coordinates_mapping = ld._disaggregate_coordinates(activities_coordinates_mapping['FC'],
                                                                                activities_coordinates_mapping['IC'])
    assert disaggregated_activities_coordinates_mapping == new_activities_coordinates_mapping


def test_get_dissimilar_coordinates_index(activities_coordinates_mapping):
    assert ld._get_dissimilar_coordinates_index(activities_coordinates_mapping['FC'],
                                                activities_coordinates_mapping['IC']) == 1


def test_get_ERE(full_IOT, activities_coordinates_with_activities):
    expected_ERE = pd.Series(np.array([19609.61370695, 11920.71802629, -40048.59665631]),
                             index=['Coking_coal', 'Crude_oil', 'Natural_gas'])
    use_categories = ['IC', 'FC']
    ressource_categories = ['IC', 'Labour_Tax']
    pd.testing.assert_series_equal(ld.get_ERE(use_categories, ressource_categories,
                                              full_IOT, activities_coordinates_with_activities),
                                   expected_ERE,
                                   check_names=False)


def test_ERE_not_balanced(full_IOT, capsys):
    unbalanced_ERE = pd.Series(np.array([0.5, 0., -40048.59665631]),
                               index=['Coking_coal', 'Crude_oil', 'Natural_gas'])
    ld.is_ERE_balanced(unbalanced_ERE)
    assert capsys.readouterr().err == "Warning : unbalanced IOT" + linebreaker + \
                                      "Coking_coal, Natural_gas" + linebreaker


def test_modify_activity_value(part_IOT, activities_coordinates_with_activities):
    IOT_uses = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'I', 'X']
    IOT_ressources = ['Coking_coal', 'Crude_oil', 'Natural_gas', 'Labour_Tax', 'Labour_income']
    IOT_data = np.array([[ 0. ,       0.      ,        0.       , 0., 19609.61370695 ],
                         [ 0. ,       0.      ,        0.       , 0., 24190.37317909 ],
                         [ 0. , 3225.19564403 ,        0.       , 0., 513333.19103917],
                         [ 0. , 9044.45950877 , 556606.98333951 , 0.,        0.      ],
                         [-100, 20587.91760946, 1267005.36419441, 0.,        0.      ]])
    expected_modified_IOT = pd.DataFrame(IOT_data, index=IOT_ressources, columns=IOT_uses)
    fill_series = pd.DataFrame(np.array([[-100., -200., -300.]]),
                               columns=['Coking_coal', 'Crude_oil', 'Natural_gas'],
                               index=['Labour_income'])
    ld.modify_activity_value(part_IOT, activities_coordinates_with_activities['Labour_income'],
                             part_IOT.loc[activities_coordinates_with_activities['Labour_income']] == 0,
                             fill_series)
    pd.testing.assert_frame_equal(part_IOT, expected_modified_IOT)


data_account_data = np.array([[0, 36613000, 0, 0],
                              [0, 142634000, -142634000, 0],
                              [-36683000, 36683000, 0, 0],
                              [0, 21618000, -21618000, 0],
                              [200125000, 64284000, 112312000, 0]])
accounts = ['OtherIndirTax_byAgent', 'Income_Tax',
            'Corporate_Tax', 'Other_Direct_Tax',
            'GFCF_byAgent']
institutions = ['Corporations', 'Government', 'Households', 'RestOfWorld']
account_table = pd.DataFrame(data_account_data, index=accounts, columns=institutions)
selected_accounts = {'Income_Tax': 'Households',
                     'Corporate_Tax': 'Corporations',
                     'GFCF_byAgent': '  RestOfWorld'}


def test_extract_accounts():
    expected_data_account = {'OtherIndirTax_byAgent': pd.Series(np.array([0, 36613000, 0, 0]),
                                                                index=institutions,
                                                                name='OtherIndirTax_byAgent'),
                             'Income_Tax': 142634000,
                             'Corporate_Tax': 3.66830000e+07,
                             'Other_Direct_Tax': pd.Series(np.array([0, 21618000, -21618000, 0]),
                                                           index=institutions,
                                                           name='Other_Direct_Tax'),
                             'GFCF_byAgent': pd.Series(np.array([200125000, 64284000, 112312000]),
                                                       index=institutions[:3],
                                                       name='GFCF_byAgent')}
    assert_dicts_equals(ld.extract_accounts(account_table,
                                            selected_accounts),
                        expected_data_account)


to_pick_accounts_ref = {'Income_Tax': 'Households',
                        'Corporate_Tax': 'Corporations'}
to_trim_accounts_ref = {'GFCF_byAgent': 'RestOfWorld'}


def test_extract_selected_accounts():
    expected_selected_accounts = {'Income_Tax': 142634000,
                                  'Corporate_Tax': 3.66830000e+07,
                                  'GFCF_byAgent': pd.Series(np.array([200125000, 64284000, 112312000]),
                                                            index=institutions[:3],
                                                            name='GFCF_byAgent')}
    assert_dicts_equals(ld.extract_selected_accounts(account_table.apply(abs),
                                                     selected_accounts),
                        expected_selected_accounts)


def test_filter_accounts_type():
    to_pick_accounts, to_trim_accounts = ld.filter_accounts_type(selected_accounts)
    assert ((to_pick_accounts == to_pick_accounts_ref) and
            (to_trim_accounts == to_trim_accounts_ref))


assertions_func = {pd.DataFrame: pd.testing.assert_frame_equal,
                   pd.Series: pd.testing.assert_series_equal,
                   pd.Index: pd.testing.assert_index_equal}


def assert_dicts_equals(left: Dict[str, Any],
                        right: Dict[str, Any]
                        ) -> bool:
    for item, left_object in left.items():
        object_type = type(left_object)
        if object_type in assertions_func:
            assertions_func[object_type](left_object, right[item])
        else:
            assert left_object == right[item]


def test_trim_selected_accounts():
    expected_trimmed_accounts = {'GFCF_byAgent': pd.Series(np.array([200125000, 64284000, 112312000]),
                                                           index=institutions[:3],
                                                           name='GFCF_byAgent')}
    assert_dicts_equals(ld.trim_selected_accounts(account_table,
                                                  to_trim_accounts_ref),
                        expected_trimmed_accounts)
