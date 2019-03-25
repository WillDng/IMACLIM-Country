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
