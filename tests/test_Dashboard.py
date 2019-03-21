# coding : utf-8

import pytest
import src.Dashboard as dashb
from src.common_utils import InputError


def test_convert_dashboard_values():
    dashb_data = iter([['H_DISAGG', 'H1'],
                       ['Nb_Iter', '2'],
                       ['CO2_footprint', 'True']])
    expected_dashb_data = iter([['H_DISAGG', 'H1'],
                                ['Nb_Iter', 2],
                                ['CO2_footprint', True]])
    assert list(dashb.convert_dashboard_values(dashb_data)) == list(expected_dashb_data)

def test_compose_duplicates_message():
    expected_duplicates_message = 'various types of disaggregation profiles of households have been selected in Dashboard\n'+\
                                'various types of resolution system have been selected in Dashboard'
    assert dashb.compose_duplicates_message (['H_DISAGG', 'System_Resol']) == expected_duplicates_message
