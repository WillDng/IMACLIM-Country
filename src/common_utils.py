# coding : utf-8

import sys
import collections
import csv
import pandas as pd
import pathlib as pl
from src.parameters import (linebreaker, file_delimiter)
from typing import (Any, Dict, Iterator, List, Union, Tuple)


def read_csv(path: pl.Path,
             delimiter: str,
             remove_blanks: bool = True) -> Iterator[List[str]]:
    mapping_raw_data = list(csv.reader(open(path), delimiter=delimiter))
    _warns_if_bad_delimiter(mapping_raw_data, path)
    if remove_blanks:
        mapping_raw_data = _remove_trailing_blanks(mapping_raw_data)
    return iter(mapping_raw_data)


def _warns_if_bad_delimiter(file_content: List[List[str]], file_path: pl.Path):
    callers_caller = sys._getframe(3).f_code.co_name
    if len(file_content[0]) == 1:
        sys.stderr.write("Warning : delimiter might not be correctly informed in " +
                         callers_caller + "() for " + str(file_path) +
                         linebreaker)


def _remove_trailing_blanks(file_content: List[List[str]]):
    clean_file_content = list()
    for row in file_content:
        row_str = file_delimiter.join(row).rstrip(file_delimiter)
        clean_file_content.append(row_str.split(file_delimiter))
    return clean_file_content


def read_dict(path: pl.Path, value_col: int, key_col: int = 0,
              delimiter: str = '|', overwrite: bool = False,
              raises: bool = False) -> Dict[str, str]:
    iter_data = _read_csv(path, delimiter)
    if not overwrite:
        iter_data, duplicates = filter_list_duplicate(iter_data,
                                                      key_col=key_col)
        if raises:
            raise_if_duplicates(duplicates, path)
    return fill_dict(iter_data, value_col, key_col)


def filter_list_duplicate(entry_iter_list: Iterator[List[Any]],
                          key_col: int = 0) -> Tuple[Iterator[List[Any]], List[str]]:
    out_list = list()
    seen_item = list()
    duplicates = list()
    for row in entry_iter_list:
        key_item = row[key_col]
        if key_item in seen_item:
            duplicates.append(key_item)
            continue
        else:
            out_list.append(row)
            seen_item.append(key_item)
    return iter(out_list), duplicates


def raise_if_duplicates(duplicates: List[str],
                        path: pl.Path) -> None:
    if duplicates:
        raise InputError(', '.join(duplicates) + ' have duplicates in ' +
                         str(path))


def fill_dict(entry_data: Iterator,
              value_col: int,
              key_col: int = 0
              ) -> Dict[str, str]:
    out_dict = dict()
    for row in entry_data:
        out_dict[row[key_col]] = row[value_col]
    return out_dict


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


def unpack_nested_dict(nested_dict):
    unpacked_dict = dict()
    for k1, v1 in nested_dict.items():
        unpacked_dict.update(v1)
    return unpacked_dict


def read_aggregation_mapping(mapping_path: pl.Path,
                             delimiter: str = ';',
                             col: Union[int, None] = None
                             ) -> Dict[str, List[str]]:
    mapping_raw = _read_csv(mapping_path,
                            delimiter=delimiter)
    return extract_aggregation_mapping(mapping_raw,
                                       col)


def extract_aggregation_mapping(aggregation_mapping: Iterator[List[str]],
                                col: Union[int, None] = None
                                ) -> Dict[str, List[str]]:
    read_mapping = dict()
    for variable_description in aggregation_mapping:
        interest_variable = variable_description[0]
        if col is None:
            categories = filter(None, variable_description[1:])
        else:
            categories = [variable_description[col]]
        for category in categories:
            read_mapping.setdefault(category, list()).append(interest_variable)
    return read_mapping


def read_table(IOT_file_path: pl.Path, **kwargs) -> pd.DataFrame:
    read_table = pd.read_csv(IOT_file_path,
                             index_col=0,
                             **kwargs)
    if read_table.empty:
        sys.stderr.write("Warning : IOT delimiter might not be correctly informed in " +
                         str(IOT_file_path) + linebreaker)
    return read_table


def flatten_list(l):
    for el in l:
        if isinstance(el, collections.abc.Sequence) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el
