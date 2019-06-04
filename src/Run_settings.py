# coding : ut-8

import pathlib as pl
import common_utils as cu
from parameters import (file_delimiter)
from typing import (Dict, Iterator, List)
import ipdb


def set_runs(study_dashb: Dict[str, str]
             ) -> Dict[str, Dict[str, str]]:
    init_calib_var = read_init_calib_variables(study_dashb['studydata_dir'] / 'Index_Imaclim_VarCalib.csv')


def read_init_calib_variables(path: pl.Path
                              ) -> Dict[str, Dict[str, str]]:
    init_calib_raw_file = cu.read_csv(path,
                                      delimiter=file_delimiter)
    init_calib_variables = extract_init_calib_variables(init_calib_raw_file)
    ipdb.set_trace()


def extract_init_calib_variables(init_calib_raw_data: Iterator[List[str]]
                                 ) -> Dict[str, Dict[str, str]]:
    out_init_calib_var = dict()
    header, headless_init_calib_raw_data = cu.separate_iterator_header(init_calib_raw_data)
    vartype_index = header.index('Type')
    for row in headless_init_calib_raw_data:
        vartype = row[vartype_index]
        if vartype not in out_init_calib_var:
            out_init_calib_var[vartype] = dict()
        out_variable = dict()
        for size in ['Row Size', 'Column Size']:
            out_variable[size] = row[header.index(size)]
        variable_name = row[header.index('Variable Name')]
        out_init_calib_var[vartype][variable_name] = out_variable
    return out_init_calib_var
