# coding : utf-8

# FIXME some OSes config do not append local directory in PYTHONPATH
# hence path_fix
import path_fix
from src import (Dashboard,
                 Loading_data_api as lda)

ISO_selection = 'FRA_update'

Dashboard = Dashboard.read_(ISO_selection)
Initial_values = lda.load_data(Dashboard)
