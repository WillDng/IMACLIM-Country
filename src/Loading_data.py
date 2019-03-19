# coding : utf-8

from src import Loading_data_lib as ld
from paths import data_dir
import ipdb

IOT_val_path = data_dir / 'IOT_Val.csv'
IOT_val = ld.read_table(IOT_val_path,
                        delimiter=';')
value_activities_mapping_path = data_dir / 'value_activities_mapping.csv'
value_activities_mapping = ld.read_activities_mapping(value_activities_mapping_path,
                                                      delimiter=',',
                                                      headers=ld.get_headers_from(IOT_val))

value_categories_coord_path = data_dir / 'value_categories_coordinates.csv'
value_categories_coord = ld.read_categories_coordinates(value_categories_coord_path,
                                                        delimiter=',')

value_coord = ld.map_categories_to_activities_coordinates(value_categories_coord,
                                                          value_activities_mapping)
value_coord = ld.disaggregate_in_coordinates(value_coord,
                                             ['FC', 'OthPart_IOT'], 'IC')

value_ressource_categories = ['IC', 'OthPart_IOT']
use_categories = ['IC', 'FC']
ld.is_IOT_balanced(use_categories, value_ressource_categories,
                   IOT_val, value_coord)
current_ERE = ld.get_ERE(use_categories, value_ressource_categories,
                         IOT_val, value_coord)
value_ressources_to_correct = {'M_value': (IOT_val.loc[value_coord['M_value']] != 0,
                                           IOT_val.loc[value_coord['M_value']] - current_ERE),
                               'Profit_margin': (IOT_val.loc[value_coord['M_value']] == 0,
                                                 IOT_val.loc[value_coord['Profit_margin']] - current_ERE)}
for ressource_to_correct, correction_info in value_ressources_to_correct.items():
    correction_condition, correction_value = correction_info
    ld.modify_activity_value(IOT_val, value_coord[ressource_to_correct],
                             correction_condition, correction_value)
ld.is_IOT_balanced(use_categories, value_ressource_categories,
                   IOT_val, value_coord)

initial_values = ld.extract_IOTs_from(IOT_val, value_coord)

#########

IOT_quantity_path = data_dir / 'IOT_Qtities.csv'
IOT_quantity = ld.read_table(IOT_quantity_path,
                             delimiter=';',
                             skipfooter=1,
                             engine='python')

quantity_activities_mapping_path = data_dir / 'quantity_activities_mapping.csv'
quantity_activities_mapping = ld.read_activities_mapping(quantity_activities_mapping_path,
                                                         delimiter=',',
                                                         headers=ld.get_headers_from(IOT_quantity))
quantity_activities_mapping = dict(value_activities_mapping, **quantity_activities_mapping)
quantity_coord_path = data_dir / 'quantity_categories_coordinates.csv'
quantity_categories_coord = ld.read_categories_coordinates(quantity_coord_path,
                                                           delimiter=',')
quantity_coord = ld.map_categories_to_activities_coordinates(quantity_categories_coord,
                                                             quantity_activities_mapping)
quantity_coord = ld.disaggregate_in_coordinates(quantity_coord,
                                                ['FC'], 'IC')
quantity_ressource_categories = ['M', 'Y']
ld.is_IOT_balanced(use_categories, quantity_ressource_categories,
                   IOT_quantity, quantity_coord)
current_ERE = ld.get_ERE(use_categories, quantity_ressource_categories,
                         IOT_quantity, quantity_coord)
quantity_uses_to_correct = {'Y': (IOT_quantity.loc[quantity_coord['Y']] != 0,
                                  IOT_quantity.loc[quantity_coord['Y']] + current_ERE),
                            'X': (IOT_quantity.loc[quantity_coord['Y']] == 0,
                                  IOT_quantity.loc[quantity_coord['X']] - current_ERE)}
for use_to_correct, correction_info in quantity_uses_to_correct.items():
    correction_condition, correction_value = correction_info
    ld.modify_activity_value(IOT_quantity, quantity_coord[use_to_correct],
                             correction_condition, correction_value)
ld.is_IOT_balanced(use_categories, quantity_ressource_categories,
                   IOT_quantity, quantity_coord)

initial_quantities = ld.extract_IOTs_from(IOT_quantity, quantity_coord)

#########


IOT_prices_path = data_dir / 'IOT_Prices.csv'
IOT_prices = ld.read_table(IOT_prices_path,
                           delimiter=';',
                           skipfooter=1,
                           engine='python')

initial_prices = ld.extract_IOTs_from(IOT_prices, quantity_coord)

#########

IOT_CO2_path = data_dir / 'IOT_CO2.csv'
IOT_CO2 = ld.read_table(IOT_CO2_path,
                        delimiter=';',
                        skipfooter=1,
                        engine='python')

CO2_activities_mapping_path = data_dir / 'CO2_activities_mapping.csv'
CO2_activities_mapping = ld.read_activities_mapping(CO2_activities_mapping_path,
                                                    delimiter=',')
CO2_activities_mapping = dict(value_activities_mapping, **CO2_activities_mapping)
CO2_categories_coord_path = data_dir / 'CO2_categories_coordinates.csv'
CO2_categories_coord = ld.read_categories_coordinates(CO2_categories_coord_path,
                                                      delimiter=',')
CO2_activities_coord = ld.map_categories_to_activities_coordinates(CO2_categories_coord,
                                                                   CO2_activities_mapping)
initial_CO2 = ld.extract_IOTs_from(IOT_CO2, CO2_activities_coord)

#########

DataAccount_path = data_dir / 'DataAccountTable.csv'
DataAccount_table = ld.read_table(DataAccount_path,
                                  delimiter=';',
                                  skipfooter=1,
                                  engine='python')
extracted_accounts = ld.extract_accounts(DataAccount_table)
selected_accounts_path = data_dir / 'DataAccountTable_params.csv'
selected_accounts = ld.read_list(selected_accounts_path,
                                 delimiter=',')
extracted_households_accounts = ld.extract_households_accounts(DataAccount_table,
                                                               selected_accounts)
initial_DataAccount = dict(extracted_accounts, **extracted_households_accounts)
# FIXME
initial_DataAccount['GFCF_byAgent'] = initial_DataAccount['GFCF_byAgent'][:3]

#########

labour_path = data_dir / 'Labour.csv'
initial_labour = ld.read_table(labour_path,
                               delimiter=';',
                               skipfooter=1,
                               engine='python')


#########

demography_path = data_dir / 'Demography.csv'
demography_table = ld.read_table(demography_path,
                                 delimiter=';',
                                 skipfooter=1,
                                 engine='python')

initial_demography = ld.extract_table_variables(demography_table,
                                                demography_table.index,
                                                demography_table.columns[0])

#########

import_rate_path = data_dir / 'IOT_Import_rate.csv'
IOT_import_rate = ld.read_table(import_rate_path,
                                delimiter=';')
import_rate_coord = ld.map_list_to_dict(use_categories, value_coord)
initial_import_rate = ld.extract_IOTs_from(IOT_import_rate, import_rate_coord)
