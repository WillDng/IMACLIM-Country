# coding : utf-8

import sys
from src.parameters import linebreaker
from typing import (Any, Dict, Iterable, List)

def read_dict(path: str, value_col: int, key_col: int = 0,
              delimiter: str='|', overwrite: bool=False,
              warn: bool=False) -> Dict[str, str]:
    iter_data = _read_csv(path, delimiter)
    if not overwrite:
        iter_data = filter_list_duplicate(iter_data,
                                          path,
                                          key_col=key_col,
                                          warn=warn)
    out_dict = dict()
    for row in iter_data:
        out_dict[row[key_col]] = row[value_col]
    return out_dict

def _read_csv(path: str, delimiter: str) -> Iterable[List[str]]:
    mapping_raw_data = list(csv.reader(open(path), delimiter=delimiter))
    _warns_if_bad_delimiter(mapping_raw_data, path)
    return iter(_remove_trailing_blanks(mapping_raw_data))

def _warns_if_bad_delimiter(file_content: List[List[str]], file_path: str):
    callers_caller = sys._getframe(3).f_code.co_name
    if len(file_content[0]) == 1:
        sys.stderr.write("Warning : delimiter might not be correctly informed in " +
                         callers_caller + "() for " + file_path +
                         linebreaker)

def filter_list_duplicate(entry_iter_list: Iterable[List[Any]],
                          file_path: str,
                          key_col: int=0,
                          warn: bool=False) -> Iterable[List[Any]]:
    out_list = list()
    seen_item = list()
    for row in entry_iter_list:
        key_item = row[key_col]
        if key_item in seen_item:
            if warn:
                sys.stderr.write('Warning : ' + key_item +
                                 ' already in ' + file_path )
            continue
        else:
            out_list.append(row)
            seen_item.append(key_item)
    return iter(out_list)
