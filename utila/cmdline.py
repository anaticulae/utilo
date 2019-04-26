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
from os import getcwd
from os.path import abspath
from os.path import exists
from os.path import isabs
from os.path import isfile
from os.path import join

from utila.logging import logging
from utila.logging import logging_error
from utila.utils import FAILURE
from utila.utils import SUCCESS

INVALID_COMMAND = 2
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
    shortcut: str = ''
    longcut: str = ''
    message: str = ''
    args: dict = field(default_factory=dict)

    def __iter__(self):
        for item in [self.shortcut, self.longcut, self.message, self.args]:
            yield item


# TODO: Add deprecation warning to Command


class Flag(Command):
    """A Flag is only on or off.

    Example:
        --all
    """
    pass


class Parameter(Command):
    """A Parameter needs data as a second argument

    Example:
        --input path
    """

    def __post_init__(self):
        assert self.longcut.startswith('--')
        self.args['dest'] = self.longcut[2:]


@dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        self.args['required'] = True


def create_parser(
        todo: list = None,
        version=None,
        inputparameter: bool = False,
        outputparameter: bool = False,
):
    """Create parser out of defined dictonary with command-line-definiton.

    Returns created argparser
    """
    if todo is None:
        todo = []
    if not isinstance(todo, list):
        todo = [todo]
    # Copy to avoid changing list. If create_parse(todo) is invoked twice,
    # changing the reference is no good idea and will produce --output, --input
    # twice.
    todo = list(todo)

    parser = ArgumentParser(prog='baw')

    if version:
        todo.append(Command('-v', '--version', 'Show version and exit.'))
        parser.__version = version

    if inputparameter:
        input_command = Command(
            '-i',
            '--input',
            'Read input data from path',
            args={
                'dest': 'input',
            },
        )
        todo.insert(0, input_command)

    if outputparameter:
        output_command = Command(
            '-o',
            '--ouput',
            'Write output to path',
            args={
                'dest': 'output',
            },
        )
        # set output after input, if not input, set output at the start
        output_position = 1 if inputparameter else 0
        todo.insert(output_position, output_command)

    for shortcut, longcut, msg, args in todo:
        shortcuts = (shortcut, longcut) if shortcut else (longcut,)
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

    if 'version' in args and args['version']:
        logging(parser.__version)
        exit(SUCCESS)

    if 'help' in args and args['help']:
        parser.print_help()
        exit(SUCCESS)

    return args


def print_help(parser, systemexit: bool = False):
    args = vars(parser.parse_args())
    need_help = not any(args.values())

    if need_help:
        parser.print_help()

    if need_help and systemexit:
        exit(FAILURE)


def sources(args):
    cwd = abspath(getcwd())
    inputpath = args.get('input')  # if key is not present, return None
    outputpath = args.get('output')

    if inputpath:
        if not isabs(inputpath):
            # Make path absolute
            inputpath = join(cwd, inputpath)
        if not exists(inputpath):
            logging_error('Input %s does not exists' % inputpath)
            exit(INVALID_COMMAND)

    if outputpath:
        if not isabs(outputpath):
            outputpath = join(cwd, outputpath)
        if isfile(outputpath):
            logging_error('Output %s must be a directory' % outputpath)
            exit(INVALID_COMMAND)
        if exists(outputpath):
            logging_error('Output %s already exists' % outputpath)
            exit(INVALID_COMMAND)
    return (inputpath, outputpath)
