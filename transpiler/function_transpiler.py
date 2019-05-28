# coding : utf-8

import argparse
import io
import pathlib as pl
import re
import sys


parser = argparse.ArgumentParser('scilab functions file to python transpilator')
parser.add_argument('--comment_char', default='//', help='character used for comments')
parser.add_argument('input_file_name', help='file with input scilab functions')
args = parser.parse_args()

comment_char = args.comment_char
python_comment_char = '# '

linebreaker = '\n'


output = sys.stdout


def transpile_scilab_functions(path_to_file: str
                               ) -> None:
    # ipdb.set_trace()
    filepath = pl.Path(path_to_file)
    read_file = open(filepath)
    parse_functions(read_file)


def parse_functions(input_file: io.TextIOWrapper
                    ) -> None:
    for line in input_file:
        if is_function_start(line):
            transpile_function(line, input_file)
        else:
            if is_comment(line):
                line = python_comment_char + line
            output.write(line)


def is_comment(line: str) -> bool:
    comment_re = re.compile('^[ \t]*' + comment_char)
    if comment_re.search(line):
        return True


function_signature_re = re.compile("^function (\[?.+\]?) = (.+\(.*\)) ?;?$")


def is_function_start(line: str) -> bool:
    if function_signature_re.search(line):
        return True


def transpile_function(line: str,
                       input_file: io.TextIOWrapper
                       ) -> str:
    new_function_signature, result = format_header(line)
    body = get_function_body(input_file)
    result = format_result(result)
    for function_part in [new_function_signature, body, result]:
        output.write(function_part)


indentation = '    '


line_re = {'\.\*': '*',
           '\t': indentation,
           ';[ \t]*$': '',
           '(?<=\w) +': ' ',
           "(?<=.)\'": '.T',
           '(?<=\w)=(?=\w)': ' = ',
           '\./': '/',
           '(?<=\w) +\( +(?=\w)': '(',
           'lambda': 'Lambda',
           '\.\^': '^',
           '(sum\(.*) ("r")': '\g<1> axis=1',
           '(sum\(.*) ("c")': '\g<1> axis=2',
           '\*\.': '*',
           '<>': '!=',
           '1:nb_Sectors-1': 'nb_Sectors',
           # '\(([\w_]+, *:)\)': '[\g<1>]',
           '\(([\w\s+]* *: *[\w\s+\(\)]* *)\)' : '[\g<1>]',
           '\.\. *$': '\\\\',
           '^ {,3}(?=\w)': indentation,
           '^ {3,100}(?=\w)': indentation,
           '^(?=\S)': indentation}


def format_header(line: str
                  ) -> str:
    result, function_name_arguments = function_signature_re.match(line).groups()
    function_name_arguments = change_lambda(function_name_arguments)
    return linebreaker * 2 + 'def ' + function_name_arguments + ':' + linebreaker, result


def change_lambda(line: str) -> str:
    return re.sub('lambda', line_re['lambda'], line)


def get_function_body(input_file: io.TextIOWrapper
                      ) -> str:
    body = str()
    line = str()
    while not is_function_end(line):
        if is_comment(line):
            line = format_comment_in_body(line)
        else:
            for pattern, replacement in line_re.items():
                line = re.sub(pattern, replacement, line)
        body += line
        line = input_file.__next__()
    return body


def format_comment_in_body(line: str) -> str:
    line = re.sub(' *', '', line)
    return indentation + python_comment_char + line


function_end_re = re.compile('endfunction')


def is_function_end(line: str) -> bool:
    if function_end_re.match(line):
        return True


function_return = indentation + 'return' + ' '


def format_result(result: str) -> str:
    result = change_lambda(result)
    return function_return + result + linebreaker


if __name__ == '__main__':
    transpile_scilab_functions(args.input_file_name)
