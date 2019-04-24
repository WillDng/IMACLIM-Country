# coding : utf-8

from src import (Dashboard,
                 Loading_data_api as lda)

ISO_selection = 'FRA_update'

Dashboard = Dashboard.read_(ISO_selection)
Initial_values = lda.load_data(Dashboard)
