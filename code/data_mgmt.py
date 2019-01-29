# coding : utf-8

import sys
import os
import pandas

linebreaker = '\n'
dir_separator = os.sep

def import_IOT(IOT_file_path, **kwargs):
	read_IOT = pandas.read_csv(IOT_file_path, 
							   index_col=0,
							   **kwargs)
	if len(get_IOT_header_from(read_IOT)) < 2:
		IOT_name = get_filename_from(IOT_file_path)
		sys.stderr.write("Warning : IOT delimiter might not be correctly informed in "+IOT_name+linebreaker)
	return read_IOT

def get_IOT_header_from(IOT):
	return IOT.columns.tolist()

def get_filename_from(path):
	return path.split(dir_separator)[-1]