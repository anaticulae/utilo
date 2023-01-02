#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import sys

import pytest
import utilatest

import utila
import utila.cli


def test_cli_parse_args(mp):
    """Create a parser with 2 parameter, pass arguments and evaluate the
    result"""
    todo = [
        utila.Parameter('-a', '--alls', 'Do all!'),
        utila.Parameter('-n', '--nothing', 'Do nothing!'),
    ]
    config = utila.cli.ParserConfiguration(
        failfastflag=True,
        verboseflag=True,
        prefix=True,
    )
    parser = utila.cli.create_parser(
        description='This is just a sample parser',
        prog='parser',
        todo=todo,
        config=config,
    )

    argv = ['parser', '--alls', '"hallo this is helmut"', '--nothing', 'aaa']
    with mp.context() as context:
        context.setattr(sys, 'argv', argv)
        parser.print_help()
        args = utila.parse(parser)
    # for verbose level
    verbose_prefix_failfast = len('--verbose --prefix --ff --cache --cprofile '
                                  '--pages --j --wait'.split())
    assert len(args) == len(todo) + verbose_prefix_failfast
    assert '--alls' in args
    assert '--nothing' in args


@pytest.mark.parametrize('prefix', [True, False])
def test_cli_prefix_activation(mp, prefix):
    todo = [
        utila.Flag(longcut='--longcut', message='display longcuts'),
    ]
    parsername = 'parser'
    config = utila.cli.ParserConfiguration(prefix=prefix,)
    parser = utila.cli.create_parser(
        description='This is just a sample parser',
        prog=parsername,
        todo=todo,
        config=config,
    )

    argv = [parsername, '--longcut']
    with mp.context() as context:
        context.setattr(sys, 'argv', argv)
        args = utila.parse(parser)
        source = utila.sources(args)

    expected_return_count = 3 if prefix else 2
    assert len(source) == expected_return_count


def test_cli_non_existing_input(tmpdir, mp):
    """Non existing input will raise an SystemExit error with value > 0"""
    result = None
    with pytest.raises(SystemExit) as result:
        create_and_run_parser(
            tmpdir,
            mp,
            ['-i', 'abc'],
        )
    assert utila.returncode(result) == 2, str(result)


def test_cli_non_existing_output(tmpdir, mp):
    """First invocation creates the folder, second invocation use it"""
    expected_out = os.path.join(tmpdir.strpath, 'abc')
    _, outpath = create_and_run_parser(
        tmpdir,
        mp,
        ['-o', 'abc'],
    )
    assert os.path.exists(expected_out), expected_out
    assert outpath == expected_out

    # invoke parser twice
    create_and_run_parser(
        tmpdir,
        mp,
        ['-o', 'abc'],
    )


def test_cli_existing_input(tmpdir, mp):
    create_and_run_parser(
        tmpdir,
        mp,
        ['-i', tmpdir.strpath],
    )


def test_cli_relative_output(tmpdir, mp):
    os.makedirs(os.path.join(tmpdir, 'abc'))
    create_and_run_parser(
        tmpdir,
        mp,
        ['-o', './abc'],
    )
    assert os.path.exists(os.path.join(tmpdir, 'abc'))


def test_cli_file_as_output(tmpdir, mp):
    utila.file_create(os.path.join(tmpdir, 'test.txt'), 'I am a file.')
    with pytest.raises(SystemExit) as result:
        create_and_run_parser(
            tmpdir,
            mp,
            ['-o', os.path.join(tmpdir, 'test.txt')],
        )
    assert utila.returncode(result) == 2, str(result)


RUN_ME = """\
#! /usr/bin/env python
import sys
sys.path.append("%s")
from utila import RequiredCommand
from utila.cli import create_parser

parser = create_parser(RequiredCommand('-a', '--alls', 'I need it all'))
parser.parse_args()
"""


def test_cli_parse_required_command_missing(tmpdir):
    runner = os.path.join(tmpdir, 'run.py')
    utila.file_create(runner, RUN_ME % utila.forward_slash(utila.ROOT))

    command = f'python "{runner}"'
    completed = utilatest.run(command, tmpdir, expect=False)

    in_stderr = 'the following arguments are required'
    assert in_stderr in completed.stderr
    assert completed.returncode > 0, str(completed)


def test_cli_parse_required_command(tmpdir):
    runner = os.path.join(tmpdir, 'run.py')
    utila.file_create(runner, RUN_ME % utila.forward_slash(utila.ROOT))
    command = f'python "{runner}" -a Samba'
    completed = utilatest.run(command, tmpdir)
    assert not completed.returncode, str(completed)


EMPTY_PARSER = """\
#! /usr/bin/env python
import sys
sys.path.append("%s")
from utila.cli import create_parser, parse, ParserConfiguration
parser = create_parser(%s)
args = parse(parser)
"""

SOURCES = """
from utila import sources

print(sources(args))
"""


@pytest.fixture
def parser_example(tmpdir):
    runner = os.path.join(tmpdir, 'empty.py')
    config = ("config=ParserConfiguration('inputparameter=True, "
              "outputparameter=True')")
    content = EMPTY_PARSER % (utila.forward_slash(utila.ROOT), config)
    utila.file_create(runner, content)
    cwd = os.path.split(tmpdir)[0]
    return cwd, runner


def test_cli_parse_empty_parser_help(parser_example):  # pylint: disable=W0621
    """Test default parser with --help"""
    cwd, runner = parser_example
    command = f'python "{runner}" --help'
    completed = utilatest.run(command, cwd)

    assert completed.returncode == utila.SUCCESS, str(completed)


def test_cli_parser_source_in_out(parser_example):  # pylint: disable=W0621
    """Test default parser with --help"""
    cwd, runner = parser_example
    utila.file_append(runner, SOURCES)
    command = f'python "{runner}" -i {runner} -o out.file'
    completed = utilatest.run(command, cwd, expect=False)
    assert completed.returncode == utila.INVALID_COMMAND, str(completed)


def test_cli_parse_empty_parser_version(parser_example):  # pylint: disable=W0621
    """Test default parser with --version"""
    cwd, runner = parser_example
    command = f'python "{runner}" --version'
    completed = utilatest.run(command, cwd, expect=False)
    assert completed.returncode == utila.INVALID_COMMAND, str(completed)


def test_cli_parse_version_parser_version(tmpdir):
    """Test version parser with --version flag"""
    version = "1.1.1"
    runner = os.path.join(tmpdir, 'version.py')

    root = utila.forward_slash(utila.ROOT)
    config = (f'version="{version}", prog="testo",'
              'config=ParserConfiguration(verboseflag=True,)')
    parser = EMPTY_PARSER % (root, config)
    utila.file_create(runner, parser)

    cmd = f'python {runner} --version'
    completed = utilatest.run(cmd, tmpdir)
    assert completed.stdout.strip() == version

    cmd = f'python {runner} --verbose --version '
    completed = utilatest.run(cmd, tmpdir)
    assert completed.stdout.strip() == f'testo {version}'


def create_and_run_parser(
    td,
    mp,
    argv,
    prefix: bool = True,
    singleinput: bool = False,
):
    prog = 'parser'
    argv = [prog] + argv
    config = utila.cli.ParserConfiguration(
        inputparameter=True,
        outputparameter=True,
        prefix=prefix,
    )
    parser = utila.cli.create_parser(
        prog=prog,
        config=config,
    )

    with mp.context() as context:
        context.setattr(sys, 'argv', argv)
        context.setattr(os, 'getcwd', lambda: str(td))  # pylint:disable=C3001
        parsed = utila.parse(parser)
        inpath, outpath, _ = utila.sources(  # pylint:disable=unbalanced-tuple-unpacking
            parsed,
            singleinput=singleinput,
        )
    return inpath, outpath


@pytest.mark.parametrize('singlefile', [True, False])
def test_cli_singlefile_input(td, mp, singlefile):
    """Test reading a file direct from input

    1. singlefile = True
        read root       ok
        read sample.txt ok
    2. singlefile = False
        read root       ok
        read sample.txt SystemExit
    """
    root = str(td)
    # Create input file
    filepath = os.path.join(root, 'sample.txt')
    utila.file_create(filepath)

    # read root
    argv = ['-i', root, '-o', root]
    inpath, _ = create_and_run_parser(
        td,
        mp,
        argv=argv,
        singleinput=True,
    )
    assert inpath == [root], 'folderinput does not deliver the right path'

    # read sample.txt
    argv = ['-i', filepath, '-o', root]
    if singlefile:
        inpath, _ = create_and_run_parser(
            td,
            mp,
            argv=argv,
            singleinput=True,
        )
        assert inpath == [filepath], 'singleinp does not deliver the right path'
    else:
        with pytest.raises(SystemExit) as result:
            argv = ['-i', filepath, '-o', root]
            create_and_run_parser(
                td,
                mp,
                argv=argv,
                singleinput=False,
            )
        assert utila.returncode(result) == utila.INVALID_COMMAND


def test_cli_sort_parameter():
    expected = [
        utila.NumberedParameter(
            shortcut='j',
            longcut='',
            message='select number of jobs',
            args={
                'dest': 'job',
                'default': 1,
                'type': int
            },
            default=1,
        ),
        utila.Flag(
            shortcut='V',
            longcut='verbose',
            message='define verbose level of logging',
            args={'action': 'count'},
        ),
        utila.Flag(
            shortcut='',
            longcut='all',
            message='',
            args={},
        ),
        utila.Flag(
            shortcut='',
            longcut='brokenworker',
            message='export brokenworker',
            args={},
        ),
        utila.Flag(
            shortcut='',
            longcut='ff',
            message='failfast: quit after the first error',
            args={},
        ),
        utila.Parameter(
            shortcut='',
            longcut='pages',
            message='shrink to given pages',
            args={
                'dest': 'pages',
                'default': ':'
            },
        ),
        utila.Parameter(
            shortcut='',
            longcut='prefix',
            message='add prefix to separate different output files',
            args={'dest': 'prefix'},
        ),
    ]
    result = utila.cli.sort(expected)
    assert result == expected, 'is not sorted correctly'


def test_evaluate_multiple_pages_flags():
    args = {'pages': ['5:10', '9', '19', '50:58']}
    pages = utila.cli.evaluate_flags(args)[2]
    expected = (5, 6, 7, 8, 9, 19, 50, 51, 52, 53, 54, 55, 56, 57)
    assert pages == expected


def test_evaluate_multiple_pages_flags_empty():
    args = {'pages': []}
    pages = utila.cli.evaluate_flags(args)[2]
    assert pages is None, pages
