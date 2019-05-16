# coding : utf-8

from src import (common_utils as cu,
                 Dashboard as ds)
import pandas as pd
from parameters import file_delimiter
import pathlib as pl
from paths import params_dir
from typing import (Dict, Iterator, List, Union)
import ipdb


filename_sep = '_'
csv_extension = '.csv'


def load_params(study_dashb: Dict[str, Union[str, int, bool]]):
    study_parameters_path = params_dir / study_dashb['region']
    # // DEFAULT VALUES OF Parameters//

    # // All general parameters - not depending on sector aggregation
    parameters = read_parameters(study_parameters_path / 'params_general.csv')

    # ///////////////////////////////////////////////////////////////
    # // All parameters 1xsect dimension - depend on aggregation profil
    # ///////////////////////////////////////////////////////////////
    sectoral_params_elements = path_to('params_sect',
                                       study_dashb)
    sectoral_params = read_params(study_parameters_path.joinpath(*sectoral_params_elements),
                                  header_name='Sectors')
    parameters.update(sectoral_params)

    # ///////////////////////////////////////////////////////////////
    # // All parameters 1x nb_Households dimension - depend on desaggregation HH profil
    # ///////////////////////////////////////////////////////////////
    households_params_filename = 'params_' + study_dashb['H_DISAGG'] + csv_extension
    households_params = read_households_params(study_dashb,
                                               study_parameters_path / households_params_filename,
                                               header_name='HH_disaggregation')
    parameters.update(households_params)

    # ///////////////////////////////////////////////////////////////
    # // All paramaters sect x sect dimension
    # ///////////////////////////////////////////////////////////////
    sectors_sectors_parameters = ['ConstrainedShare_IC', 'CarbonTax_Diff_IC', 'phi_IC']
    for sectors_sectors_parameter in sectors_sectors_parameters:
        sectors_sectors_elements = path_to(sectors_sectors_parameter,
                                           study_dashb)
        sectors_sectors_params = cu.read_table(study_parameters_path.joinpath(*sectors_sectors_elements),
                                               delimiter=file_delimiter)
        parameters[sectors_sectors_parameter] = sectors_sectors_params
    ipdb.set_trace()


def read_parameters(parameters_path: str
                    ) -> Dict[str, float]:
    parameters_raw = cu._read_csv(parameters_path,
                                  delimiter=file_delimiter)
    parameters_data = ds.filter_comment_in_dashboard(parameters_raw)
    parameters_data = _convert_parameters_values(parameters_data)
    return ds.nested_list_to_dict(parameters_data,
                                  value_col=1)


def _convert_parameters_values(parameters_data: Iterator[List[List[str]]]
                               ) -> Iterator[List[List[Union[str, float]]]]:
    out_parameters_data = list()
    for row in parameters_data:
        try:
            value = row[1]
        except IndexError:
            value = None
        if is_float(value):
            row[1] = float(value)
        out_parameters_data.append(row)
    return iter(out_parameters_data)


def is_float(entry: str) -> bool:
    try:
        float(entry)
        return True
    except (ValueError, TypeError):
        return False


def path_to(filename_core: str,
            dashb: Dict[str, Union[str, float, bool]]
            ) -> str:
    path_arguments = list()
    filename = filename_core
    aggregation_level = dashb['AGG_type']
    if aggregation_level:
        path_arguments.append(aggregation_level)
        filename = filename_core + filename_sep + aggregation_level
    filename += csv_extension
    path_arguments.append(filename)
    return path_arguments


def read_params(params_path: pl.Path,
                header_name: str
                ) -> Dict[str, pd.Series]:
    out_params = dict()
    params_data = read_filter_to_dict(params_path)
    headers = params_data.pop(header_name)
    for parameter, parameter_value in params_data.items():
        out_params[parameter] = pd.Series(parameter_value,
                                          index=headers,
                                          name=parameter)
    return out_params


def read_filter_to_dict(params_path: pl.Path
                        ) -> Dict[str, Union[List[str], str]]:
    params_data = ds.read_and_filtler_csv(params_path,
                                          delimiter=file_delimiter)
    return ds.nested_list_to_dict(params_data)


def read_households_params(dashb: Dict[str, Union[str, float, bool]],
                           params_path: pl.Path,
                           header_name: str
                           ) -> Dict[str, pd.Series]:
    if dashb['H_DISAGG'] == 'HH1':
        households_params = read_filter_to_dict(params_path)
        del households_params[header_name]
        return households_params
    else:
        return read_params(params_path,
                           header_name=header_name)
