#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""
This module provides helper methods to create a command line parser tool.
The purpose of this module is to write less code and use less time in
maintaining the interface.

Example:
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
    create_parser([PUSH, RELEASE])
"""

import os
from argparse import ArgumentParser
from dataclasses import dataclass
from dataclasses import field

from utila.logging import logging
from utila.logging import logging_error
from utila.utils import SUCCESS

INVALID_COMMAND = 2
"""Returncode when application is invoked with invalid command.
See posix standard."""


@dataclass
class Command:
    """Basic class for creation further `Flag`'s or `Parameter`."""
    shortcut: str = ''
    longcut: str = ''
    message: str = ''
    """message to display when invoking --help"""
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
        #pylint:disable=unsupported-assignment-operation
        self.args['dest'] = self.longcut


@dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        self.args['required'] = True


VERBOSE = 'verbose'

COMMANDS = [
    Parameter(
        longcut='prefix',
        message='add prefix to separate different output files',
    ),
    Flag(
        args={'action': 'count'},
        longcut=VERBOSE,
        message='define how verbose logging is',
        shortcut='V',
    ),
]


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
    # Copy to avoid changing the source list. If create_parse(todo) is invoked
    # twice, changing the reference is no good idea and will produce --output,
    # --input twice.
    todo = list(todo)
    todo.extend(COMMANDS)

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
        if longcut and not longcut.startswith('--'):
            longcut = '--%s' % longcut

        if longcut:
            shortcuts = (shortcut, longcut) if shortcut else (longcut,)
        else:
            # no longcut is defined
            shortcuts = (shortcut,)

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
            shortcut='i',
            message='Read input data from path',
            args={
                'dest': 'input',
            },
        )
        todo.append(input_command)

    if outfile:
        output_command = Command(
            shortcut='o',
            message='Write output to path',
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


def sources(args, *, singleinput: bool = False, verbose: bool = False):
    """Parse the in- and outport from given command line args

    The input- and output-path must be a directory. If singleinput flag is
    activated, a file is addtionaly allowed as input.

    Args:
        args(str): arguments, passed by command line
        singleinput(bool): allow a single file instead of a directory as
                           input
        verbose(bool): if True, evaluate the verbose level
    Returns:
        (input, output): path(str) to in-/ and output-location
    """
    cwd = os.path.abspath(os.getcwd())
    inputpath = args.get('input')  # if key is not present, return None
    outputpath = args.get('output')
    prefix = args.get('prefix')

    if inputpath:
        if not os.path.isabs(inputpath):
            # Make path absolute
            inputpath = os.path.join(cwd, inputpath)
        if not singleinput:
            if os.path.isfile(inputpath):
                logging_error('Input %s must be a directory' % inputpath)
                exit(INVALID_COMMAND)
        if not os.path.exists(inputpath):
            logging_error('Input %s does not exists' % inputpath)
            exit(INVALID_COMMAND)

    if outputpath:
        if not os.path.isabs(outputpath):
            outputpath = os.path.join(cwd, outputpath)
        if os.path.isfile(outputpath):
            logging_error('Output %s must be a directory' % outputpath)
            exit(INVALID_COMMAND)
        if not os.path.exists(outputpath):
            logging('Creating: %s' % outputpath)
            os.makedirs(outputpath)

    if verbose:
        verb = int(args[VERBOSE]) if args[VERBOSE] else 0
        return (inputpath, outputpath, prefix, verb)
    return (inputpath, outputpath, prefix)
