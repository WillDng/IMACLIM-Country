# coding : utf-8

import sys
import os
import csv
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

def read_classification_from(IOT_classification_path, delimiter='|'):
	reader = csv.reader(open(IOT_classification_path), 
						delimiter=delimiter)
	IOT_classification = dict()
	for row in reader:
		group = row[1]
		if group not in IOT_classification:
			IOT_classification[group] = set()
		IOT_classification[group].add(row[0])
	return IOT_classification

def slice_(IOT, field_headers):
	sliced_IOT = IOT.loc[field_headers]
	if sliced_IOT.isnull().values.any():
		sys.stderr.write("Warning : IOT headers might be ill informed informed"+linebreaker)
	return sliced_IOT
