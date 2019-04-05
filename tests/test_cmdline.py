#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from argparse import Namespace

from utila import Command
from utila import create_parser
from utila import parse


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
