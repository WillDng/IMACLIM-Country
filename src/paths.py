# coding : utf-8

import pathlib

basedir = pathlib.Path(__file__).parents[1]

data_dir = basedir.joinpath('new_format', 'data')
# data_dir = basedir  / 'data'

study_frames_dir = basedir.joinpath('new_format', 'study_frames')
# study_frames_dir = basedir / 'study_frames'
