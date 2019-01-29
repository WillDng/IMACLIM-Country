# coding: utf-8

import pytest
import pandas
from code import data_mgmt
from code.data_mgmt import linebreaker, dir_separator

good_IOT_path = 'tests/mock_data/IOT_Val.csv'
IOT_delimiter = ';'

@pytest.fixture()
def good_IOT():
	return pandas.read_csv(good_IOT_path, 
						   delimiter=IOT_delimiter,
						   index_col=0)

@pytest.fixture()
def bad_delimiter_IOT():
	return pandas.read_csv(good_IOT_path)

def test_import_IOT(good_IOT):
	read_IOT = data_mgmt.import_IOT(good_IOT_path, delimiter=';')
	assert read_IOT.equals(good_IOT)

def test_import_IOT_non_correct_column_header():
	read_IOT = data_mgmt.import_IOT(good_IOT_path)
	assert all([isinstance(header, str) for header in read_IOT.index])

def test_get_filename_from_path():
	filename = data_mgmt.get_filename_from(good_IOT_path)
	assert filename == good_IOT_path.split(dir_separator)[-1]

def test_import_bad_delimiter_IOT(capsys):
	data_mgmt.import_IOT(good_IOT_path)
	IOT_name = data_mgmt.get_filename_from(good_IOT_path)
	captured = capsys.readouterr()
	assert captured.err == "Warning : IOT delimiter might not be correctly informed in "+IOT_name+linebreaker

def test_get_IOT_header_from(good_IOT):
	header = data_mgmt.get_IOT_header_from(good_IOT)
	IOT_header = next(open(good_IOT_path)).rstrip(linebreaker).split(IOT_delimiter)[1:]
	assert header == IOT_header