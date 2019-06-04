# coding : utf-8

# FIXME some OSes config do not append local directory in PYTHONPATH
# hence path_fix
import path_fix
from src import (Dashboard,
                 Loading_data as ld,
                 Loading_params as lp,
                 Run_settings as rst)

ISO_selection = 'FRA_update'

dashboard = Dashboard.read_(ISO_selection)
initial_values = ld.load_data(dashboard)
parameters = lp.load_params(dashboard)
runs = rst.set_runs(dashboard)
