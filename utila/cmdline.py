#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
from argparse import ArgumentParser
from dataclasses import dataclass
from dataclasses import field
from os import makedirs
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


@dataclass
class Flag(Command):
    """A Flag is only on or off.

    Example:
        --all
    """


@dataclass
class Parameter(Command):
    """A Parameter needs data as a second argument

    Example:
        --input path
    """

    def __post_init__(self):
        self.args['dest'] = self.longcut


@dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        self.args['required'] = True


def create_parser(
        todo: list = None,
        version=None,
        inputparameter: bool = False,
        outputparameter: bool = False,
        prog: str = '',
        description: str = '',
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

    parser = ArgumentParser(prog=prog, description=description)

    if version:
        todo.append(Flag('-v', 'version', 'Show version and exit.'))
        parser.__version = version

    io_ports = create_io_ports(inputparameter, outputparameter)
    if io_ports:
        # set io ports to the top
        todo = io_ports + todo

    for shortcut, longcut, msg, args in todo:
        # support defining shortcut without -
        if shortcut and not shortcut.startswith('-'):
            shortcut = '-%s' % shortcut
        # support defining longcut without --
        if not longcut.startswith('--'):
            longcut = '--%s' % longcut
        shortcuts = (shortcut, longcut) if shortcut else (longcut,)
        add = parser.add_argument
        if args:
            args['help'] = msg
            add(*shortcuts, **args)
        else:
            add(*shortcuts, action='store_true', help=msg)
    return parser


def create_io_ports(infile: bool = False, outfile: bool = False):
    todo = []
    if infile:
        input_command = Command(
            'i',
            'input',
            'Read input data from path',
            args={
                'dest': 'input',
            },
        )
        todo.append(input_command)

    if outfile:
        output_command = Command(
            'o',
            'ouput',
            'Write output to path',
            args={
                'dest': 'output',
            },
        )
        todo.append(output_command)
    return todo


def parse(parser: ArgumentParser):
    """Parse arguments from sys-args and return the result as dictonary."""
    args = vars(parser.parse_args())
    if 'version' in args and args['version']:
        logging(parser.__version)
        exit(SUCCESS)

    return args


def sources(args):
    """In- and outport must be a directory"""
    cwd = abspath(os.getcwd())
    input_path = args.get('input')  # if key is not present, return None
    output_path = args.get('output')

    if input_path:
        if not isabs(input_path):
            # Make path absolute
            input_path = join(cwd, input_path)
        if isfile(input_path):
            logging_error('Input %s must be a directory' % input_path)
            exit(INVALID_COMMAND)
        if not exists(input_path):
            logging_error('Input %s does not exists' % input_path)
            exit(INVALID_COMMAND)

    if output_path:
        if not isabs(output_path):
            output_path = join(cwd, output_path)
        if isfile(output_path):
            logging_error('Output %s must be a directory' % output_path)
            exit(INVALID_COMMAND)
        if not exists(output_path):
            logging('Creating: %s' % output_path)
            makedirs(output_path)
    return (input_path, output_path)
