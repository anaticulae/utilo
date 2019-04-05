#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from argparse import ArgumentParser
from dataclasses import dataclass
from dataclasses import field

from utila.utils import FAILURE
"""
Exampple:
    PUSH = Command('-p', '--publish', 'Push release to repository')
    RELEASE = Command(
        '-r', '--release', 'Test and tag commit as new release', {
            'nargs': '?',
            'const': 'auto',
            'choices': [
                'major',
                'minor',
                'patch',
                'noop',
                'auto',
            ],
        })
"""


@dataclass
class Command:
    shortcut: str
    longcut: str
    message: str
    args: dict = field(default_factory=dict)

    def __iter__(self):
        for item in [self.shortcut, self.longcut, self.message, self.args]:
            yield item


@dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        self.args['required'] = True


def create_parser(todo: list = None):
    """Create parser out of defined dictonary with command-line-definiton.

    Returns created argparser
    """
    if todo is None:
        todo = []
    if not isinstance(todo, list):
        todo = [todo]

    parser = ArgumentParser(prog='baw')

    for shortcut, longcut, msg, args in todo:
        shortcuts = (shortcut, longcut)
        add = parser.add_argument
        if args:
            args['help'] = msg
            add(*shortcuts, **args)
        else:
            add(*shortcuts, action='store_true', help=msg)
    return parser


def parse(parser: ArgumentParser):
    """Parse arguments from sys-args and return the result as dictonary."""
    args = vars(parser.parse_args())
    return args


def print_help(parser, systemexit: bool = False):
    args = vars(parser.parse_args())
    need_help = not any(args.values())

    if need_help:
        parser.print_help()

    if need_help and systemexit:
        exit(FAILURE)
