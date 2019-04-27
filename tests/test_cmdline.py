#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import sys

from pytest import fixture
from pytest import raises

from utila import INVALID_COMMAND
from utila import ROOT
from utila import SUCCESS
from utila import Parameter
from utila import create_parser
from utila import file_append
from utila import file_create
from utila import forward_slash
from utila import parse
from utila import sources
from utila.test import run
from utila.test import skip_not_virtual


def test_parse_args(monkeypatch):
    """Create a parser with 2 parameter, pass arguments and evaluate the
    result"""
    todo = [
        Parameter('-a', '--all', 'Do all!'),
        Parameter('-n', '--nothing', 'Do nothing!'),
    ]
    parser = create_parser(
        description='This is just a sample parser',
        prog='parser',
        todo=todo,
    )

    argv = ['parser', '--all', '"hallo this is helmut"', '--nothing', 'aaa']
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', argv)
        parser.print_help()
        args = parse(parser)

    assert len(args) == len(todo)
    assert '--all' in args
    assert '--nothing' in args


def test_non_existing_input(tmpdir, monkeypatch):
    """Non existing input will raise an SystemExit error with value > 0"""
    result = None
    with raises(SystemExit) as result:
        create_and_run_parser(
            tmpdir,
            monkeypatch,
            ['-i', 'abc'],
        )
    assert 'SystemExit: 2' in str(result)


def test_non_existing_output(tmpdir, monkeypatch):
    """First invocation creates the folder, second invocation use it"""
    expected_out = os.path.join(tmpdir.strpath, 'abc')
    _, outpath = create_and_run_parser(
        tmpdir,
        monkeypatch,
        ['-o', 'abc'],
    )
    assert os.path.exists(expected_out), expected_out
    assert outpath == expected_out

    # invoke parser twice
    create_and_run_parser(
        tmpdir,
        monkeypatch,
        ['-o', 'abc'],
    )


def test_existing_input(tmpdir, monkeypatch):
    create_and_run_parser(
        tmpdir,
        monkeypatch,
        ['-i', tmpdir.strpath],
    )


def test_relative_output(tmpdir, monkeypatch):
    os.makedirs(os.path.join(tmpdir, 'abc'))
    create_and_run_parser(
        tmpdir,
        monkeypatch,
        ['-o', '/abc'],
    )
    assert os.path.exists(os.path.join(tmpdir, 'abc'))


def test_file_as_output(tmpdir, monkeypatch):
    file_create(os.path.join(tmpdir, 'test.txt'), 'I am a file.')
    with raises(SystemExit) as result:
        create_and_run_parser(
            tmpdir,
            monkeypatch,
            ['-o', os.path.join(tmpdir, 'test.txt')],
        )
    assert 'SystemExit: 2' in str(result)


RUN_ME = """\
#! /usr/bin/env python
import sys
sys.path.append("%s")
from utila import RequiredCommand
from utila import create_parser

parser = create_parser(RequiredCommand('-a', '--all', 'I need it all'))
parser.parse_args()
"""


@skip_not_virtual
def test_parse_required_command_missing(tmpdir):
    runner = os.path.join(tmpdir, 'run.py')
    file_create(runner, RUN_ME % forward_slash(ROOT))

    command = 'python "%s"' % runner
    completed = run(command, tmpdir)

    in_stderr = 'the following arguments are required'
    assert in_stderr in completed.stderr
    assert completed.returncode > 0, str(completed)


@skip_not_virtual
def test_parse_required_command(tmpdir):
    runner = os.path.join(tmpdir, 'run.py')
    file_create(runner, RUN_ME % forward_slash(ROOT))

    command = 'python "%s" -a Samba' % runner
    completed = run(command, tmpdir)

    assert completed.returncode == 0, str(completed)


EMPTY_PARSER = """\
#! /usr/bin/env python
import sys
sys.path.append("%s")
from utila import create_parser, parse
parser = create_parser(%s)
args = parse(parser)
"""

SOURCES = """
from utila import sources

print(sources(args))
"""


@fixture
def parser_example(tmpdir):
    runner = os.path.join(tmpdir, 'empty.py')
    content = EMPTY_PARSER % (forward_slash(ROOT),
                              'inputparameter=True, outputparameter=True')
    file_create(runner, content)
    cwd = os.path.split(tmpdir)[0]
    return cwd, runner


@skip_not_virtual
def test_parse_empty_parser_help(parser_example):
    """Test default parser with --help"""
    cwd, runner = parser_example
    command = 'python "%s" --help' % runner
    completed = run(command, cwd)

    assert completed.returncode == SUCCESS, str(completed)


@skip_not_virtual
def test_parser_source_in_out(parser_example):
    """Test default parser with --help"""
    cwd, runner = parser_example
    file_append(runner, SOURCES)

    command = 'python "%s" -i %s -o out.file' % (runner, runner)
    completed = run(command, cwd)

    assert completed.returncode == INVALID_COMMAND, str(completed)


@skip_not_virtual
def test_parse_empty_parser_version(parser_example):
    """Test default parser with --version"""
    cwd, runner = parser_example
    command = 'python "%s" --version' % runner
    completed = run(command, cwd)

    assert completed.returncode == INVALID_COMMAND, str(completed)


@skip_not_virtual
def test_parse_version_parser_version(tmpdir):
    """Test version parser with --version flag"""
    version = "1.1.1"
    runner = os.path.join(tmpdir, 'version.py')

    parser = EMPTY_PARSER % (forward_slash(ROOT), 'version="%s"' % version)
    file_create(runner, parser)

    command = 'python "%s" --version' % runner
    completed = run(command, tmpdir)
    assert completed.stdout.strip() == version
    assert completed.returncode == SUCCESS, str(completed)


def create_and_run_parser(tmpdir, monkeypatch, argv):
    prog = 'parser'
    argv = [prog] + argv
    parser = create_parser(
        prog=prog,
        inputparameter=True,
        outputparameter=True,
    )

    def getcwd():
        return tmpdir.strpath

    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', argv)
        context.setattr(os, 'getcwd', getcwd)
        parsed = parse(parser)
        print(parsed)
        inpath, outpath = sources(parsed)
    return inpath, outpath
