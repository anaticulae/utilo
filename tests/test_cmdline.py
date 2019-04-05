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

from utila import Command
from utila import create_parser
from utila import forward_slash
from utila import parse
from utila import ROOT
from utila.file import file_create
from utila.test import run
from utila.test import skip_not_virtual
from utila.utils import NEWLINE


def test_parse_args(monkeypatch):
    todo = [
        Command('-a', '--all', 'Do all!'),
        Command('-n', '--nothing', 'Do nothing!'),
    ]

    parser = create_parser(todo=todo)

    def parsevalue():
        return Namespace(all='I am All', nothing='I am Nothing')

    with monkeypatch.context() as m:
        m.setattr(parser, 'parse_args', parsevalue)
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
