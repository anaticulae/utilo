# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys
from contextlib import contextmanager
from functools import partial
from os import makedirs
from os.path import exists
from os.path import join

from pytest import mark
from pytest import raises

import utila
from utila import FAILURE
from utila import File
from utila import create_step
from utila import featurepack
from utila import file_create
from utila import file_remove
from utila import returncode
from utila.feature import PAGES_FLAG
from utila.utils import SUCCESS

WORKPLAN = [
    create_step(
        'first_cli_step',
        [
            File('first'),
            File('second', 'html'),
            File('third'),
        ],
        (('result'),),
    ),
]

EXAMPLE = """
def work(first: str, second: str, third: str)->str:
    return first

def name():
    return 'first_cli_step'
"""

EXAMPLE_WITH_PAGE = """
def work(second: str, third: str, pages: int)->str:
    # Ensure that passing pages works correctly!
    assert pages == tuple(range(5,10)), pages
    return str(pages)

def name():
    return 'cli_with_pages'
"""

EXAMPLE_WITH_PAGE_WORKPLAN = [
    create_step(
        'cli_with_pages',
        [
            File('second', 'html'),
            File('third'),
        ],
        (('result'),),
    ),
]

EXAMPLE_MULTIPLE_RETURNVALUES = """
def work(test : str) -> list:
    result = []
    result.append('Hello')
    result.append('Mr')
    result.append('Tom')
    result.append('.')
    print('work')
    return result

def name():
    return 'multistep'
"""

EXAMPLE_MULTIPLE_RETURNVALUES_WORKPLAN = [
    create_step(
        'multistep',
        [
            File('third'),
        ],
        (('pages/view_*', 'html'),),
    ),
]

INVALID_WORKPLAN = [
    create_step(
        'cli_with_pages',
        [
            # Pages parameter is not allowed in workplan, it is delivered
            # automatically if needed
            File(PAGES_FLAG),
            File('second', 'html'),
            File('third'),
        ],
        (('result'),),
    ),
]


def cli_example(testdir, example=EXAMPLE):
    root = str(testdir)
    example_path = join(root, 'example')
    makedirs(example_path)
    featurepath = join(example_path, 'features')
    makedirs(featurepath)

    cli_example_feature = join(featurepath, 'cli_example.py')
    file_create(cli_example_feature, example)

    cli_example_feature_init = join(featurepath, '__init__.py')
    file_create(cli_example_feature_init, '')

    cli_example_init = join(example_path, '__init__.py')
    file_create(cli_example_init, '')

    sys.path.append(root)

    # create test files
    file_create('first.yaml')
    file_create('second.html')
    file_create('third.yaml')

    return (root, featurepath)


PROCESSNAME = 'cli_example'


def create_runner(
        featurepack_=featurepack,
        description='',
        featurepackage='example.features',
        multiprocessed=False,
        name=PROCESSNAME,
        pages=True,
        version='beta',
        workplan=None,
):
    if workplan is None:
        workplan = list(WORKPLAN)
    runner = partial(
        featurepack_,
        description=description,
        featurepackage=featurepackage,
        multiprocessed=multiprocessed,
        name=name,
        pages=pages,
        version=version,
        workplan=workplan,
    )
    return runner


Runner = create_runner()  # pylint:disable=C0103


@contextmanager
def run_cli(root, monkeypatch, cmdline, runner=Runner):
    """Run test command line interface

    cmdline(str/[str]): commands to execute
    """
    cmdline = cmdline.split()
    with monkeypatch.context() as context:
        with raises(SystemExit) as result:
            context.setattr(sys, 'argv', [PROCESSNAME] + cmdline)
            runner(root=root)
    yield result


def test_workplan_invalid(testdir, monkeypatch, capsys):  # pylint:disable=W0621
    invalid = create_runner(workplan=INVALID_WORKPLAN)
    root, _ = cli_example(testdir, EXAMPLE_WITH_PAGE)
    with run_cli(root, monkeypatch, '--all', runner=invalid) as result:
        out, err = capsys.readouterr()
    assert 'parameter `pages` is not allowed' in err
    assert returncode(result) == FAILURE, str(out) + str(err)


def test_workplan_valid_with_pages(testdir, monkeypatch, capsys):  # pylint:disable=W0621
    valid = create_runner(workplan=EXAMPLE_WITH_PAGE_WORKPLAN)
    root, _ = cli_example(testdir, EXAMPLE_WITH_PAGE)
    command = '--all --pages=5:10'
    with run_cli(root, monkeypatch, command, runner=valid) as result:
        out, err = capsys.readouterr()
    assert returncode(result) == SUCCESS, str(out) + str(err)


def test_cli_example(testdir, monkeypatch, capsys):  # pylint:disable=W0621
    root, _ = cli_example(testdir)

    with run_cli(root, monkeypatch, '-h') as result:
        captured = capsys.readouterr().out

    assert 'inputs:' in captured, str(captured)
    assert 'outputs:' in captured, str(captured)

    assert returncode(result) == SUCCESS, str(result)


@mark.parametrize('command', [
    '--all',
    '--pages=0:10',
])
def test_cli_example_all(testdir, monkeypatch, capsys, command):
    """Run cli example with commands"""
    root, _ = cli_example(testdir)

    with run_cli(root, monkeypatch, '%s -VVV' % command) as result:
        out, err = capsys.readouterr()
    assert len(out) > 50, str(out) + str(err)
    assert not err, str(err)

    assert returncode(result) == SUCCESS, str(result)


def test_cli_print_processing_step(testdir, monkeypatch, capsys):
    """Ensure that processing: process_step is printed when running
    working step."""
    root, _ = cli_example(testdir)

    with run_cli(root, monkeypatch, '--all -VVV') as result:
        out = capsys.readouterr().out

    assert returncode(result) == SUCCESS, str(result)
    assert len(out) > 100
    assert 'processing: first_cli_step' in out, utila.log_raw(out)


@mark.parametrize(
    'create_missing_input',
    [True, False],
)
def test_cli_multiple_input(
        testdir,
        monkeypatch,
        capsys,
        create_missing_input: bool,
):
    cli_example(testdir)
    root = str(testdir)
    # remove file out of first example to test multiple -i sources
    first_yaml = join(root, 'first.yaml')
    assert exists(first_yaml), first_yaml
    file_remove(first_yaml)
    assert not exists(first_yaml), first_yaml

    second_input = join(root, 'second')
    makedirs(second_input)

    if create_missing_input:
        second_first_yaml = join(second_input, 'first.yaml')
        assert not exists(second_first_yaml), second_first_yaml
        file_create(second_first_yaml)
        assert exists(second_first_yaml), second_first_yaml

    # run
    inputcmd = '-i %s -i %s -VVV' % (root, second_input)
    with run_cli(root, monkeypatch, inputcmd) as result:
        out, err = capsys.readouterr()

    # check
    expected_result = SUCCESS if create_missing_input else FAILURE
    error_message = '%s\n%s\n%s' % (result, out, err)
    assert returncode(result) == expected_result, error_message


def test_cli_multiple_input_with_double_input(
        testdir,
        monkeypatch,
        capsys,
):
    """Test that resources exists in both input source"""
    cli_example(testdir)
    root = str(testdir)

    second_input = join(root, 'second')
    makedirs(second_input)

    third_path = join(second_input, 'third.yaml')
    file_create(third_path)
    assert exists(third_path)

    inputcmd = '-i %s -i %s -VVV' % (root, second_input)
    with run_cli(root, monkeypatch, inputcmd) as result:
        out, err = capsys.readouterr()
    assert returncode(result) == SUCCESS, str(result) + str(out) + str(err)


MULTI_RUNNER = create_runner(multiprocessed=True)


@mark.parametrize(
    'jobs',
    [
        1,  # single processed
        10,
    ],
)
def test_cli_multiple_jobs(
        testdir,
        monkeypatch,
        capsys,
        jobs: int,
):
    cli_example(testdir)
    root = str(testdir)

    cmd = '-j %d --all' % jobs
    with run_cli(root, monkeypatch, cmd, MULTI_RUNNER) as result:
        out, err = capsys.readouterr()
    error_message = '%s\n%s\n%s' % (result, out, err)
    assert returncode(result) == SUCCESS, str(error_message)


def test_workplan_multiple_returnvalues(testdir, monkeypatch, capsys):  # pylint:disable=W0621
    invalid = create_runner(workplan=EXAMPLE_MULTIPLE_RETURNVALUES_WORKPLAN)
    root, _ = cli_example(testdir, EXAMPLE_MULTIPLE_RETURNVALUES)
    with run_cli(root, monkeypatch, '--all', runner=invalid) as result:
        out, err = capsys.readouterr()
    assert returncode(result) == SUCCESS, str(out) + str(err)
    path = str(testdir)
    pages = os.path.join(path, 'cli_example__multistep_pages')
    assert os.path.exists(pages), str(pages)
    # test to create multiple return files
    created_files = os.listdir(pages)
    # 4 html files must be created
    assert len(created_files) == 4
