#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""This module provides helper methods to create a command line parser
tool. The purpose of this module is to write less code and use less time
in maintaining the interface.

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

import argparse
import contextlib
import dataclasses
import os
import sys

from utila.file import make_absolute
from utila.logger import error
from utila.logger import log
from utila.pages import parse_pages
from utila.utils import ALL_PAGES
from utila.utils import SUCCESS

INVALID_COMMAND = 2
"""Returncode when application is invoked with invalid command.
See posix standard."""


@dataclasses.dataclass
class Command:
    """Basic class for creation further `Flag`'s or `Parameter`."""
    shortcut: str = ''
    longcut: str = ''
    message: str = ''
    """message to display when invoking --help"""
    args: dict = dataclasses.field(default_factory=dict)

    def __iter__(self):
        for item in [self.shortcut, self.longcut, self.message, self.args]:
            yield item


@dataclasses.dataclass
class Flag(Command):
    """A Flag is only on or off.

    Example:
        --all
    """


@dataclasses.dataclass
class Parameter(Command):
    """A Parameter needs data as a second argument

    Example:
        --input path
    """

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        self.args['dest'] = self.longcut


@dataclasses.dataclass
class Number(Parameter):

    default: int = 1

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        assert self.longcut or self.shortcut, 'no short or longcut defined'
        if 'dest' not in self.args:  # do not overwrite user defined flags
            self.args['dest'] = self.longcut if self.longcut else self.shortcut
        self.args['default'] = self.default
        self.args['type'] = type(self.default)


@dataclasses.dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        self.args['required'] = True


VERBOSE = 'verbose'


def create_parser(  # pylint:disable=R1260
        todo: list = None,
        version=None,
        description: str = '',
        prog: str = '',
        *,
        failfastflag: bool = False,
        flags: list = None,
        inputparameter: bool = False,
        multiprocessed: bool = False,
        outputparameter: bool = False,
        pages: bool = False,
        prefix: bool = False,
        profileflag: bool = False,
        quiteflag: bool = False,
        verboseflag: bool = False,
) -> argparse.ArgumentParser:
    """Create parser out of defined dictonary with command-line-definiton.

    Args:
        description(str): description text of --help invocation
        failfastflag(bool): if True --ff option is added to parser
        flags(list): list of `Command`s to add
        inputparameter(bool): if true, default input parameter is active
        multiprocessed(bool): add parameter to use more than one processor
        outputparameter(bool): if true, default output parameter is active
        pages(bool): add --pages flag to select processed pages
        prefix(bool): if true, default prefix is active
        profileflag(bool): if True --profile option is added
        prog(str): name of application `prog --help`
        quiteflag(bool): if True add option to suppress logging
        todo(list): extend default parser with todo list
        verboseflag(bool): if True add option to control verbosity of logging
        version(str): current version of parser applicatin
    Returns:
        created argparser
    """
    flags = flags[:] if flags is not None else []

    todo = prepare_todo(
        todo,
        failfastflag=failfastflag,
        flags=flags,
        multiprocessed=multiprocessed,
        pages=pages,
        prefix=prefix,
        profileflag=profileflag,
        quiteflag=quiteflag,
        verboseflag=verboseflag,
    )

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog=prog,
    )

    if version:
        todo.append(Flag('-v', 'version', 'show version and exit.'))
        parser.__version = version

    io_ports = create_io_ports(inputparameter, outputparameter)
    if io_ports:
        # set io ports to the top
        todo = io_ports + todo

    def use_todo(parser, todo):
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

            if args:
                args['help'] = msg
                parser.add_argument(*shortcuts, **args)
            else:
                parser.add_argument(*shortcuts, action='store_true', help=msg)

    use_todo(parser, todo)

    return parser


MULTI_FLAG = 'job'
PAGES_FLAG = 'pages'


def prepare_todo(
        todo,
        *,
        multiprocessed: bool,
        verboseflag: bool,
        failfastflag: bool,
        pages: bool,
        prefix: bool,
        quiteflag: bool,
        flags: list = None,
        profileflag: bool = False,
):
    todo = todo if todo else []
    if not isinstance(todo, list):
        todo = [todo]
    # Copy to avoid changing the source list. If create_parse(todo) is invoked
    # twice, changing the reference is no good idea and will produce --output,
    # --input twice.
    todo = list(todo)

    flags = flags if flags else []
    for item in flags:
        try:
            longcut, message = item
        except ValueError:
            longcut, message = item, ''
        flag = Flag(
            longcut=f'--{longcut}',
            message=message,
        )
        todo.insert(0, flag)

    if profileflag:
        profilecmd = Flag(
            longcut='profile',
            message='profile feature step execution',
        )
        todo.insert(0, profilecmd)

    if prefix:
        prefixcommand = Parameter(
            longcut='prefix',
            message='add prefix to separate different output files',
        )
        todo.insert(0, prefixcommand)

    if multiprocessed:
        multicmd = Number(
            shortcut=MULTI_FLAG[0],
            default=1,
            message='select number of used jobs',
            args={'dest': MULTI_FLAG})
        todo.insert(0, multicmd)

    if pages:
        # TODO: pages flag in def work is only possible as the last parameter
        # BUG
        page = Parameter(
            longcut=PAGES_FLAG,
            message='run computation on given pages',
            args={
                'dest': PAGES_FLAG,
                'default': ':',
            },
        )
        todo.insert(0, page)

    if verboseflag:
        todo.append(
            Flag(
                args={
                    'action': 'count',
                },
                longcut=VERBOSE,
                message='define verbose level of logging',
                shortcut='V',
            ))

    if failfastflag:
        todo.append(
            Flag(
                longcut='ff',
                message='failfast: quit after the first error',
            ))

    if quiteflag:
        todo.append(Flag(longcut='quite', message='suppress logging'))

    todo = sort(todo)
    return todo


def sort(items):
    """Sort commands alphabetically. Sort by show- or longcut."""
    sorter = lambda item: item.shortcut.lower()\
                          if item.shortcut\
                          else item.longcut.lower()
    result = sorted(items, key=sorter)
    return result


def create_io_ports(infile: bool = False, outfile: bool = False):
    todo = []
    if infile:
        input_command = Command(
            shortcut='i',
            message='read input data from path',
            args={
                'dest': 'input',
                'action': 'append'  # support multiple -i
            },
        )
        todo.append(input_command)

    if outfile:
        output_command = Command(
            shortcut='o',
            message='write output to path',
            args={
                'dest': 'output',
            },
        )
        todo.append(output_command)
    return todo


def parse(parser: argparse.ArgumentParser):
    """Parse arguments from sys-args and return the result as dictonary."""
    args = vars(parser.parse_args())
    if 'version' in args and args['version']:
        log(parser.__version)
        exit(SUCCESS)

    return args


def sources(
        args,
        *,
        singleinput: bool = False,
        verbose: bool = False,
) -> tuple:
    """Parse the in- and outport from given command line args

    The input- and output-path must be a directory. If singleinput flag is
    activated, a file is addtionaly allowed as input.

    The argparser supports multiple input locations. If the same input is
    passed twice, only the first one is used. The inputs will returned
    alphabetically as a list.

    Args:
        args(str): arguments, passed by command line
        singleinput(bool): allow a single file instead of a directory as
                           input
        verbose(bool): if True, evaluate the verbose level
    Returns:
        (input, output): path(str) to in-/ and output-location
    """
    cwd = os.path.abspath(os.getcwd())
    # multiple inputs are possible
    inputpaths = args.get('input')  # if key is not present, return None
    outputpath = args.get('output')

    prefix = args.get('prefix', False)

    if inputpaths:
        # make path absolute
        inputpaths = [make_absolute(item) for item in inputpaths]
        # make unique and sort alphabetically
        inputpaths = sorted(list(set(inputpaths)))
        for inputpath in inputpaths:
            if not singleinput:
                if os.path.isfile(inputpath):
                    error('Input %s must be a directory' % inputpath)
                    exit(INVALID_COMMAND)
            if not os.path.exists(inputpath):
                error('Input %s does not exists' % inputpath)
                exit(INVALID_COMMAND)

    if outputpath:
        if not os.path.isabs(outputpath):
            outputpath = os.path.join(cwd, outputpath)
        if os.path.isfile(outputpath):
            error('Output %s must be a directory' % outputpath)
            exit(INVALID_COMMAND)
        if not os.path.exists(outputpath):
            log('Creating: %s' % outputpath)
            os.makedirs(outputpath)

    # run application in current working directory if not paths are provided
    if not inputpaths:
        inputpaths = [os.getcwd()]
    if not outputpath:
        outputpath = os.getcwd()

    result = [inputpaths, outputpath]
    if prefix is not False:
        result.append(prefix)
    if verbose:
        try:
            verb = int(args[VERBOSE])
        except (KeyError, TypeError):
            verb = 0
        result.append(verb)
    return tuple(result)


def evaluate_flags(args, multiprocessed: bool):
    processes = 1 if not multiprocessed else args.get(MULTI_FLAG)
    with contextlib.suppress(KeyError):
        del args[MULTI_FLAG]

    failfast = args.get('ff', False)
    with contextlib.suppress(KeyError):
        del args['ff']

    profiling = args.get('profile', False)
    with contextlib.suppress(KeyError):
        del args['profile']

    pages = parse_pages(args.get(PAGES_FLAG, ALL_PAGES))
    with contextlib.suppress(KeyError):
        del args[PAGES_FLAG]

    return processes, failfast, pages, profiling


def is_userflag(flag: str) -> bool:
    """Check if `flag` is passed as user argument

    Args:
        flag(str): passed by user argument --flag or flag
    Returns:
        True if flag is passed in user argument else False
    """
    assert flag

    if flag in sys.argv:
        return True
    if f'--{flag}' in sys.argv:
        return True
    return False


def userflag_to_arg(flag: str):
    flag = flag.strip()
    return flag.split('--')[-1]
