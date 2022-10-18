#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
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
import re
import sys

import utila

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


Commands = list[Command]


@dataclasses.dataclass
class Flag(Command):
    """A Flag is only on or off.

    Example:
        --all
    """


@dataclasses.dataclass
class FlagCounted(Flag):
    """\
    Example: -VV => --verbose level 2
    """

    def __post_init__(self):
        self.args['action'] = 'count'  # pylint:disable=E1137


@dataclasses.dataclass
class Parameter(Command):
    """A Parameter needs data as a second argument

    Example:
        --input path
    """

    def __post_init__(self):
        self.args['dest'] = self.longcut  # pylint:disable=E1137


@dataclasses.dataclass
class ParameterAppended(Parameter):

    def __post_init__(self):
        super().__post_init__()
        self.args['default'] = []  # pylint:disable=E1137
        self.args['action'] = 'append'  # pylint:disable=E1137


@dataclasses.dataclass
class NumberedParameter(Parameter):

    default: int = 1

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        assert self.longcut or self.shortcut, 'no short or longcut defined'
        if 'dest' not in self.args:  # pylint:disable=E1135
            # do not overwrite user defined flags
            self.args['dest'] = self.longcut if self.longcut else self.shortcut
        self.args['default'] = self.default
        self.args['type'] = type(self.default)


@dataclasses.dataclass
class RequiredCommand(Command):

    def __post_init__(self):
        #pylint:disable=unsupported-assignment-operation
        self.args['required'] = True


VERBOSE = 'verbose'


@dataclasses.dataclass
class ParserConfiguration:  # pylint:disable=R0902
    failfastflag: bool = False
    flags: list = dataclasses.field(default_factory=list)
    inputparameter: bool = False
    singleinput: bool = False
    multiprocessed: bool = True
    outputparameter: bool = False
    pages: bool = True
    prefix: bool = False
    cprofile: bool = True
    profileflag: bool = False
    quiteflag: bool = False
    verboseflag: bool = True
    configflag: bool = False
    cacheflag: bool = True
    waitingflag: bool = True

    @staticmethod
    def all_off():
        """\
        Ensure that all options are off:
        >>> 'True' not in str(ParserConfiguration.all_off())
        True
        """
        result = ParserConfiguration()
        for key, value in vars(result).items():
            if not isinstance(value, bool):
                continue
            # turn every bool off
            setattr(result, key, False)
        return result


class DescriptionHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Increase optional width of parameter column."""

    def __init__(self, prog):
        super().__init__(
            prog=prog,
            max_help_position=80,
        )


def create_parser(
    todo: list = None,
    config: ParserConfiguration = None,
    description: str = '',
    prog: str = '',
    version=None,
) -> argparse.ArgumentParser:
    """Create parser out of defined dictionary with command-line-definition.

    Args:
        config(ParserConfiguration): collections of creation flags
        description(str): description text of --help invocation
        prog(str): name of application `prog --help`
        todo(list): extend default parser with todo list
        version(str): current version of parser application
    Returns:
        Created argparser.
    """
    if config is None:
        config = ParserConfiguration()

    todo = prepare_todo(todo, config=config)

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=DescriptionHelpFormatter,
        prog=prog,
    )

    if config.cacheflag:
        todo.append(Flag('--cache', message='use cached data'))

    if config.waitingflag:
        todo.append(
            NumberedParameter(
                longcut='wait',
                message='wait(seconds) if required resources are not ready yet',
                default=0,  # seconds
            ))

    if version:
        todo.append(Flag('-v', 'version', 'show version and exit'))
        parser.__version = version

    io_ports = create_io_ports(
        config.inputparameter,
        config.outputparameter,
        config.configflag,
        config.singleinput,
    )
    if io_ports:
        # set io ports to the top
        todo = io_ports + todo

    add_todo_to_parser(parser, todo)
    return parser


def add_todo_to_parser(parser, todo):
    for shortcut, longcut, msg, args in todo:
        # support defining shortcut without -
        if shortcut and not shortcut.startswith('-'):
            shortcut = f'-{shortcut}'
        # support defining longcut without --
        if longcut and not longcut.startswith('--'):
            longcut = f'--{longcut}'
        if longcut:  # pylint:disable=W0160
            shortcuts = (shortcut, longcut) if shortcut else (longcut,)
        else:
            # no longcut is defined
            shortcuts = (shortcut,)
        if args:
            args['help'] = msg
            parser.add_argument(*shortcuts, **args)
        else:
            parser.add_argument(*shortcuts, action='store_true', help=msg)


MULTI_FLAG = 'job'
PAGES_FLAG = 'pages'

MULTI_JOBS_DEFAULT = 8


def prepare_todo(
    todo,
    *,
    config: ParserConfiguration = None,
):
    todo = todo if todo else []
    if not isinstance(todo, list):
        todo = [todo]
    # Copy to avoid changing the source list. If create_parse(todo) is invoked
    # twice, changing the reference is no good idea and will produce --output,
    # --input twice.
    todo = todo[:]
    todo.extend(flags_to_parameter(config.flags))
    # create parser
    if config.cprofile:
        profilecmd = Flag(
            longcut='cprofile',
            message='use cprofile and write binary',
        )
        todo.insert(0, profilecmd)
    if config.profileflag:
        profilecmd = Flag(
            longcut='profile',
            message='measure runtime and print to console',
        )
        todo.insert(0, profilecmd)
    if config.prefix:
        prefixcommand = Parameter(
            longcut='prefix',
            message='add prefix to separate different output files',
        )
        todo.insert(0, prefixcommand)
    if config.multiprocessed:
        multicmd = Parameter(
            shortcut=MULTI_FLAG[0],
            longcut=MULTI_FLAG,
            # default=1,
            message='select number of jobs; use auto to select os.cpu_count',
            args={
                'dest': MULTI_FLAG,
                'default': 1,
            },
        )
        todo.insert(0, multicmd)
    if config.pages:
        # TODO: pages flag in def work is only possible as the last parameter
        # BUG
        page = ParameterAppended(
            longcut=PAGES_FLAG,
            message='shrink to given pages',
        )
        todo.insert(0, page)
    if config.verboseflag:
        todo.append(
            FlagCounted(
                longcut=VERBOSE,
                message='define verbose level of logging',
                shortcut='V',
            ))
    if config.failfastflag:
        todo.append(
            Flag(
                longcut='ff',
                message='failfast: quit after the first error',
            ))
    if config.quiteflag:
        todo.append(Flag(
            longcut='quite',
            message='suppress logging',
        ))
    todo = sort(todo)
    return todo


def flags_to_parameter(flags):
    todo = []
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
    return todo


def sort(items):
    """Sort commands alphabetically. Sort short and longcut after."""

    def sorter(item):
        if item.shortcut:
            return f'--{item.shortcut.lower()}'
        return f'-{item.longcut.lower()}'

    result = sorted(items, key=sorter)
    return result


def create_io_ports(
    infile: bool = False,
    outfile: bool = False,
    config: bool = False,
    singleinput: bool = False,
):
    todo = []
    if infile:
        input_command = ParameterAppended(
            shortcut='i',
            longcut='input',
            message='read data from path',
        )
        if singleinput:
            input_command.args['required'] = True  # pylint:disable=E1137
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
    if config:
        config_command = Command(
            shortcut='c',
            message='read config from path',
            args={
                'dest': 'config',
            },
        )
        todo.append(config_command)
    return todo


DEACTIVATED = (None, None)


def parse(parser: argparse.ArgumentParser):
    """Parse arguments from sys-args and return the result as dictionary.

    Disable -f! --flags! with acclamation mark.
    """
    # divide in activate and disable commands
    enable, disable = split_args(sys.argv)
    # remove disabling commands out of sys args to avoid problems with
    # `parse_args`.
    sys.argv = enable
    # verify version and/or verbose before parsing to avoid conflicts with
    # required resources when using e.g. `abel --version --verbose`
    if '--version' in sys.argv or '-v' in sys.argv:
        version = ''
        if isverbose(sys.argv):
            assert parser.prog, 'missing cli.prog flag'
            version = f'{parser.prog} '
        try:
            version += parser.__version
        except AttributeError:
            utila.error('missing version flag')
            sys.exit(utila.INVALID_COMMAND)
        utila.log(version)
        sys.exit(utila.SUCCESS)
    args = vars(parser.parse_args())
    # use disable with None
    args = {
        key: value if key not in disable else DEACTIVATED
        for key, value in args.items()
    }
    if isverbose(sys.argv):
        verbose = min((args['verbose'], 3))
        utila.level_setup(utila.Level(verbose))
    return args


def isverbose(args) -> bool:
    pattern = '--verbose -V -VV -VVV'.split()
    result = any(item in args for item in pattern)
    return result


DISABLE_PATTERN = r'^[-]{1,2}(?P<text>[\w\-\_^!]+?)(?:[!])$'


def split_args(items):
    """Divide between activation and deactivation commands.

    >>> split_args(['--enable_me', '--disable!', '-d!'])
    (['--enable_me'], ['disable', 'd'])
    """
    enable, disable = [], []
    for item in items:
        matched = re.match(DISABLE_PATTERN, item)
        if matched:
            disable.append(matched['text'])
        else:
            enable.append(item)
    return enable, disable


def sources(  # pylint:disable=too-complex,too-many-branches
    args,
    *,
    singleinput: bool = False,
    use_cwd: bool = True,
    verbose: bool = False,
) -> tuple:
    """Parse the in- and outport from given command line args

    The input- and output-path must be a directory. If singleinput flag
    is activated, a file is additionally allowed as input.

    The argparser supports multiple input locations. If the same input
    is passed twice, only the first one is used. The inputs will be
    returned as alphabetically sorted list.

    Args:
        args(str): arguments, passed by command line
        singleinput(bool): allow a single file instead of a directory as
                           input
        use_cwd(bool): if True replace missing in- or outpath with
                       current working direction. If not return None.
        verbose(bool): if True, evaluate the verbose level
    Returns:
        (input, output): path(str) to in-/ and output-location
    """
    cwd = os.path.abspath(os.getcwd())
    # multiple inputs are possible
    inputpaths = args.get('input', None)
    outputpath = args.get('output', None)
    # use prefix
    prefix = args.get('prefix', False)
    # verify input paths
    if inputpaths:
        # make path absolute
        inputpaths = [utila.make_absolute(item) for item in inputpaths]
        # make unique and sort alphabetically
        inputpaths = sorted(list(set(inputpaths)))
        for inputpath in inputpaths:
            if not singleinput:
                if os.path.isfile(inputpath):
                    utila.error(f'Input {inputpath} must be a directory')
                    sys.exit(INVALID_COMMAND)
            if not os.path.exists(inputpath):
                utila.error(f'Input {inputpath} does not exists')
                sys.exit(INVALID_COMMAND)
    if outputpath:
        if not os.path.isabs(outputpath):
            outputpath = os.path.join(cwd, outputpath)
        if os.path.isfile(outputpath):
            utila.error(f'Output {outputpath} must be a directory')
            sys.exit(INVALID_COMMAND)
        if not os.path.exists(outputpath):
            try:
                os.makedirs(outputpath)
            except FileExistsError:
                # avoid race condition if some other thread creates this
                # folder before.
                utila.log(f'use: {outputpath}')
            else:
                utila.log(f'creating: {outputpath}')
    # run application in current working directory if no path's are provided
    if not inputpaths and use_cwd:
        inputpaths = [os.getcwd()]
    if not outputpath and use_cwd:
        outputpath = os.getcwd()
    # prepare output
    result = [inputpaths, outputpath]
    if prefix is not False:  # pylint:disable=C2001
        result.append(prefix)
    if verbose:
        try:
            verb = int(args[VERBOSE])
        except (KeyError, TypeError):
            verb = 0
        result.append(verb)
    return tuple(result)


def evaluate_flags(args, multiprocessed: bool = False):
    processes = processcount(args, multiprocessed)
    with contextlib.suppress(KeyError):
        del args[MULTI_FLAG]
    failfast = args.get('ff', False)
    with contextlib.suppress(KeyError):
        del args['ff']
    cprofile = args.get('cprofile', False)
    with contextlib.suppress(KeyError):
        del args['cprofile']
    profiling = args.get('profile', False)
    with contextlib.suppress(KeyError):
        del args['profile']
    wait = args.get('wait', 0)
    with contextlib.suppress(KeyError):
        del args['wait']
    # evaluate multiple --pages
    pages = pages_fromargs(args)
    with contextlib.suppress(KeyError):
        del args[PAGES_FLAG]
    return processes, failfast, pages, cprofile, profiling, wait


def processcount(args: dict, multiprocessed: bool = False) -> int:
    """\
    >>> processcount(dict(job=5), multiprocessed=True)
    5
    >>> processcount(None, multiprocessed=False)
    1
    """
    processes = 1
    if not multiprocessed:
        return processes
    selected = args.get(MULTI_FLAG)
    if str(selected).lower() == 'auto':
        # convert to string to avoid converting error when passing int
        processes = os.cpu_count() if os.cpu_count() else MULTI_JOBS_DEFAULT
    else:
        try:
            processes = int(selected)
        except ValueError:
            utila.error(f'invalid process count: {selected}')
            sys.exit(utila.INVALID_COMMAND)
    return processes


def pages_fromargs(args) -> tuple:
    """Extract list of pages number out of user input args.

    >>> pages_fromargs({'pages':[0, 5,'10:15'], 'inpath':'...',})
    (0, 5, 10, 11, 12, 13, 14)
    """
    pages = args.get(PAGES_FLAG, [utila.ALL_PAGES])
    joined = utila.from_tuple(pages, separator=',')
    result = utila.parse_pages(joined)
    return result


def isuserflag(flag: str) -> bool:
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
    """\
    >>> userflag_to_arg('--iamflag')
    'iamflag'
    >>> userflag_to_arg('already_flag')
    'already_flag'
    """
    flag = flag.strip()
    return flag.split('--')[-1]
