# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys
from contextlib import contextmanager
from functools import partial
from os import makedirs
from os.path import exists
from os.path import join

from pytest import fixture
from pytest import mark
from pytest import raises

from utila import FAILURE
from utila import File
from utila import create_step
from utila import featurepack
from utila import file_create
from utila import file_remove
from utila import returncode
from utila.utils import SUCCESS

WORKPLAN = [
    create_step(
        'cli_example',
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
    return 'cli_example'
"""


@fixture
def cli_example(testdir):
    root = str(testdir)
    example = join(root, 'example')
    makedirs(example)
    featurepath = join(example, 'features')
    makedirs(featurepath)

    cli_example_feature = join(featurepath, 'cli_example.py')
    file_create(cli_example_feature, EXAMPLE)

    cli_example_feature_init = join(featurepath, '__init__.py')
    file_create(cli_example_feature_init, '')

    cli_example_init = join(example, '__init__.py')
    file_create(cli_example_init, '')

    sys.path.append(root)

    # create test files
    file_create('first.yaml')
    file_create('second.html')
    file_create('third.yaml')

    return (root, featurepath)


PROCESSNAME = 'cli_example'

Runner = partial(
    featurepack,
    workplan=WORKPLAN,
    featurepackage='example.features',
    name=PROCESSNAME,
    description='',
    version='beta',
)


@contextmanager
def run_cli(root, monkeypatch, cmdline, runner=Runner):
    """Run test command line interface

    Args:
        root(str):
        monkeypatch:
        cmdline(str/[str]): commands to execute
    """
    cmdline = cmdline.split()
    with monkeypatch.context() as context:
        with raises(SystemExit) as result:
            context.setattr(sys, 'argv', [PROCESSNAME] + cmdline)
            runner(root=root)
    yield result


def test_cli_example(testdir, monkeypatch, capsys, cli_example):
    root, _ = cli_example

    with run_cli(root, monkeypatch, '-h') as result:
        captured = capsys.readouterr().out

    assert 'inputs:' in captured, str(captured)
    assert 'outputs:' in captured, str(captured)

    assert returncode(result) == SUCCESS, str(result)


def test_cli_example_all(testdir, monkeypatch, capsys, cli_example):
    """Run every feature step with --all flag"""
    root, _ = cli_example

    with run_cli(root, monkeypatch, '--all -VVV') as result:
        out, err = capsys.readouterr()
    assert len(out) > 50, str(out)
    assert not err, str(err)

    assert returncode(result) == SUCCESS, str(result)


@mark.parametrize(
    'create_missing_input',
    [True, False],
)
def test_cli_multiple_input(
        testdir,
        monkeypatch,
        capsys,
        cli_example,
        create_missing_input: bool,
):
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


MultiRunner = partial(
    featurepack,
    description='',
    featurepackage='example.features',
    multiprocessed=True,
    name=PROCESSNAME,
    version='beta',
    workplan=WORKPLAN,
)


@mark.parametrize(
    'processes',
    [
        1,  # single processed
        10,
    ],
)
def test_cli_multiple_processes(
        testdir,
        monkeypatch,
        capsys,
        cli_example,
        processes: int,
):
    root = str(testdir)

    cmd = '--processes %d --all' % processes
    with run_cli(root, monkeypatch, cmd, MultiRunner) as result:
        out, err = capsys.readouterr()
    error_message = '%s\n%s\n%s' % (result, out, err)
    assert returncode(result) == SUCCESS, str(error_message)
