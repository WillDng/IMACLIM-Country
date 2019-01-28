# coding : utf-8

import sys
import pandas

def import_IOT(IOT_file_path, **kwargs):
	read_IOT = pandas.read_csv(IOT_file_path, index_col=0, **kwargs)
	if len(get_IOT_header_from(read_IOT)) < 2:
		sys.stderr.write("Warning : IOT delimiter might not be correctly informed\n")
	return read_IOT

def get_IOT_header_from(IOT):
	return IOT.columns.tolist()