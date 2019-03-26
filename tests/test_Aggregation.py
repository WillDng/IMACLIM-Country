# coding : utf-8

from src import Aggregation

def test_extract_aggregation():
    iter_aggregattion = iter([['','AGG_SNBC2','AGG_MetMin','AGG_IndEner'],
                              ['a', 'b', 'c', 'd'],
                              ['e', 'f', 'g', 'h'],
                              ['i', 'j', 'k', 'l']])
    expected_aggregation = {'AGG_SNBC2' : {'a':'b', 'e':'f', 'i':'j'},
                            'AGG_MetMin': {'a':'c', 'e':'g', 'i':'k'},
                            'AGG_IndEner': {'a':'d', 'e':'h', 'i':'l'}}
    assert Aggregation.extract_agg(iter_aggregattion) == expected_aggregation


def test_complete_missing_keys():
    headers = ['a', 'b', 'c', 'd']
    dict_to_complete = {'a':'b', 'e':'f', 'i':'j'}
    expected_completed_dict = {'a':'b', 'e':'f', 'i':'j',
                               'b':'b', 'c':'c', 'd':'d'}
    assert Aggregation.complete_missing_keys(dict_to_complete, headers)
