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
from os.path import basename
from os.path import join

from pytest import fixture
from pytest import raises

from utila import File
from utila import create_step
from utila import featurepack
from utila import file_create
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
def run_cli(root, monkeypatch, cmdline):
    cmdline = cmdline.split()
    with monkeypatch.context() as context:
        with raises(SystemExit) as result:
            context.setattr(sys, 'argv', [PROCESSNAME] + cmdline)
            Runner(root=root)
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
