# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys
from os import makedirs
from os.path import join

from pytest import fixture
from pytest import mark
from pytest import raises

from utila import FAILURE
from utila import SUCCESS
from utila import create_step
from utila import featurepack
from utila import file_create
from utila import returncode

WORKER = """
from typing import Tuple
def work(one_input: str) -> Tuple[str, str]:
    return {'first': '', 'second': ''}
"""

WORKER_WITH_WRONG_RETURNVALUE = """
from typing import Tuple
def work(one_input: str) -> Tuple[str, str]:
    return {'first': ''}
"""

WORKER_WITH_NO_RETURNVALUE = """
from typing import Tuple
def work(one_input: str) -> Tuple[str, str]:
    pass
"""

WORKER_WITH_EXCEPTION = """
from typing import Tuple
def work(one_input: str) -> Tuple[str, str]:
    raise ValueError
"""

WORKER_WITH_WRONG_INPUT = """
from typing import Tuple
def work() -> Tuple[str, str]:
    return {'first': '', 'second': ''}
"""


def workplan(name: str = 'complete_worker'):
    plan = [
        create_step(
            name,
            [
                ('decider_border_hitthebox', 'hits'),
            ],
            (
                ('result', 'html'),
                'error',
            ),
        ),
    ]

    return plan


PROCESS_NAME = 'feedback_decider_border'


def pack(plan, root, featurepackage):
    description = 'generate html view for overlapping content'
    version = '1.0.0'
    executed = featurepack(
        workplan=plan,
        root=root,
        featurepackage=featurepackage,
        name=PROCESS_NAME,
        description=description,
        version=version,
    )
    return executed


@fixture
def featureexample(testdir):
    root = str(testdir)
    featurepackage = 'feedback.features.border'
    feature_path = join(root, featurepackage.replace('.', '/'))
    makedirs(feature_path)
    file_create(join(root, '__init__.py'))
    file_create(join(root, 'feedback/__init__.py'))
    file_create(join(root, 'feedback/features/__init__.py'))
    file_create(join(feature_path, '__init__.py'))

    file_create(
        join(feature_path, 'incomplete_worker.py'), """
def work():
    return 'work'
    """)
    file_create(
        join(feature_path, 'complete_worker.py'), """
from utila import Flag
def name():
    return 'complete_worker'
def commandline():
    return Flag(longcut=name(), message='export the html result of %s' % name())
from typing import Tuple
def work(path : str) -> Tuple[str, str]:
    return 'work completed', 'Error'
    """)
    file_create('decider_border_hitthebox__hits.yaml', '')
    return root, featurepackage


# pylint:disable=W0621
def test_featurepack_without_input(featureexample, monkeypatch):
    root, package = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage=package)
        assert returncode(result) == FAILURE


def test_featurepack_with_broken_feature(featureexample, monkeypatch):
    """Skip broken worker"""
    root, package = featureexample
    # create the broken feature
    file_create(join(package.replace('.', '/'), 'broken_worker.py'))

    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage=package)
        assert returncode(result) == FAILURE


@mark.parametrize(
    'name,worker', [
        ('worker_with_exception', WORKER_WITH_EXCEPTION),
        ('worker_with_no_returnvalue', WORKER_WITH_NO_RETURNVALUE),
        ('worker_with_wrong_input', WORKER_WITH_WRONG_INPUT),
        ('worker_with_wrong_returnvalue', WORKER_WITH_WRONG_RETURNVALUE),
    ],
    ids=[
        'worker_with_expection',
        'worker_with_no_returnvalue',
        'worker_with_wrong_input',
        'worker_with_wrong_returnvalue',
    ])
def test_featurepack_with_broken_worker(  #pylint:disable=W0621
        featureexample,
        monkeypatch,
        name,
        worker,
):
    root, package = featureexample
    featurepath = join(root, package.replace('.', '/'))
    # create feature
    file_create(join(
        featurepath,
        '%s.py' % name,
    ), worker)
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)

        with raises(SystemExit) as result:
            pack(workplan(name), root=root, featurepackage=package)
        assert returncode(result) == FAILURE


def test_featurepack(featureexample, monkeypatch):  #pylint:disable=W0621
    root, package = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage=package)
        assert returncode(result) == SUCCESS


PDF_PARSER = """
from utila import Flag
def name():
    return 'parser'

def commandline():
    return Flag(longcut=name(), message='export the html result of %s' % name())

def work(pdffile : str) -> str:
    return 'parsed_file'
"""


def test_feature_featurepack_workplan_pdf_parser(testdir, monkeypatch):
    """Test featurepack with multiple input via *.PDF"""
    # TODO: Clean up test creating process
    root = str(testdir)
    featurepackage = 'feedback.features'
    processname = 'pdfparser'
    feature_path = join(root, featurepackage.replace('.', '/'))
    makedirs(feature_path)
    file_create(join(root, '__init__.py'))
    file_create(join(root, 'feedback/__init__.py'))
    file_create(join(root, 'feedback/features/__init__.py'))
    file_create(join(feature_path, 'parser.py'), PDF_PARSER)

    examplepath = join(root, 'example')
    makedirs(examplepath)
    file_create(join(examplepath, 'test.pdf'), 'this pdf is empty')

    workplan = [
        create_step(
            'parser',
            [
                ('*', 'PDF'),
            ],
            (('result'),),
        ),
    ]
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [
            processname,
            '-i',
            examplepath,
            '-o',
            root,
        ])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            context.syspath_prepend(root)
            featurepack(
                workplan,
                root,
                featurepackage,
                name='parsi',
                description='Description',
                version='1.0.0',
                singleinput=True,
            )
    assert returncode(result) == SUCCESS
