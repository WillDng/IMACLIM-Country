import os
import sys

dir_separator = os.sep
current_pythonpath = sys.path
sys.path.append(dir_separator.join(current_pythonpath[0].split(dir_separator)[:-1]))
