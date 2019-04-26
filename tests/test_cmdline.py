#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from argparse import Namespace
from os.path import join
from os.path import split

import pytest

from utila import INVALID_COMMAND
from utila import NEWLINE
from utila import ROOT
from utila import SUCCESS
from utila import Command
from utila import create_parser
from utila import file_append
from utila import file_create
from utila import forward_slash
from utila import parse
from utila.test import run
from utila.test import skip_not_virtual


def test_parse_args(monkeypatch):
    todo = [
        Command('-a', '--all', 'Do all!'),
        Command('-n', '--nothing', 'Do nothing!'),
    ]

    parser = create_parser(todo=todo)

    def parsevalue():
        return Namespace(all='I am All', nothing='I am Nothing')

    with monkeypatch.context() as context:
        context.setattr(parser, 'parse_args', parsevalue)
        args = parse(parser)

    assert len(args) == 2
    assert 'all' in args
    assert 'nothing' in args


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
    runner = join(tmpdir, 'run.py')
    file_create(runner, RUN_ME % forward_slash(ROOT))

    command = 'python "%s"' % runner
    completed = run(command, tmpdir)

    IN_STDERR = 'the following arguments are required'
    assert IN_STDERR in completed.stderr
    assert completed.returncode > 0, str(completed)


@skip_not_virtual
def test_parse_required_command(tmpdir):
    runner = join(tmpdir, 'run.py')
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


@pytest.fixture
def parser_example(tmpdir):
    runner = join(tmpdir, 'empty.py')
    content = EMPTY_PARSER % (forward_slash(ROOT),
                              'inputparameter=True, outputparameter=True')
    file_create(runner, content)
    cwd = split(tmpdir)[0]
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

    assert completed.returncode == SUCCESS, str(completed)


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
    VERSION = "1.1.1"
    runner = join(tmpdir, 'version.py')

    PARSER = EMPTY_PARSER % (forward_slash(ROOT), 'version="%s"' % VERSION)
    file_create(runner, PARSER)

    command = 'python "%s" --version' % runner
    completed = run(command, tmpdir)
    assert completed.stdout.strip() == VERSION
    assert completed.returncode == SUCCESS, str(completed)
