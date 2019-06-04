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
from typing import Tuple

from pytest import fixture
from pytest import mark
from pytest import raises

from utila import FAILURE
from utila import SUCCESS
from utila import create_step
from utila import featurepack
from utila import file_create

#pylint:disable=W0621,W0613


def worker(one_input: str) -> Tuple[str, str]:
    return {'first': '', 'second': ''}


def worker_with_wrong_returnvalue(one_input: str) -> Tuple[str, str]:
    return {'first': ''}


def worker_with_no_returnvalue(one_input: str) -> Tuple[str, str]:
    pass


def worker_with_exception(one_input: str) -> Tuple[str, str]:
    raise ValueError


def worker_with_wrong_input() -> Tuple[str, str]:
    return {'first': '', 'second': ''}


def workplan(worker):

    # pylint:disable=invalid-name
    FEATURE_NAME = 'hitthebox_view'
    plan = [
        create_step(FEATURE_NAME, worker, [
            ('decider_border_hitthebox', 'hits'),
        ], (
            ('result', 'html'),
            'error',
        )),
    ]

    return plan


PROCESS_NAME = 'feedback_decider_border'


def pack(plan, featurepath):
    # pylint:disable=invalid-name
    DESCRIPTION = 'generate html view for overlapping content'
    VERSION = '1.0.0'
    executed = featurepack(
        workplan=plan,
        feature_path=featurepath,
        feature_package='feedback.features.border',
        name=PROCESS_NAME,
        description=DESCRIPTION,
        version=VERSION,
    )
    return executed


@fixture
def featureexample(testdir):
    root = str(testdir)
    feature_path = join(root, 'feedback/features/border')
    makedirs(feature_path)
    file_create(join(root, '__init__.py'))
    file_create(join(root, 'feedback/__init__.py'))
    file_create(join(root, 'feedback/features/__init__.py'))
    file_create(join(feature_path, '__init__.py'))
    # file_create(join(feature_path, 'broken_worker.py'))

    file_create(
        join(feature_path, 'working_worker.py'), """
from utila import Flag
def name():
    return 'worker'
def commandline():
    return Flag(longcut=name(), message='export the html result of %s' % name())
def work():
    return 'work'
    """)
    file_create('decider_border_hitthebox__hits.yaml', '')
    return root, feature_path


def test_featurepack_without_input(featureexample, monkeypatch):
    root, path = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(worker), path)
        assert returncode(result) == FAILURE


def test_featurepack_with_broken_feature(featureexample, monkeypatch):
    """Skip broken worker"""
    root, path = featureexample
    # create the broken feature
    file_create(join(path, 'broken_worker.py'))

    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(worker), path)
        assert returncode(result) == FAILURE


@mark.parametrize('worker', [
    worker_with_exception,
    worker_with_no_returnvalue,
    worker_with_wrong_input,
    worker_with_wrong_returnvalue,
])
def test_featurepack_with_broken_worker(featureexample, monkeypatch, worker):
    root, path = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)

        with raises(SystemExit) as result:
            pack(workplan(worker), path)
        assert returncode(result) == FAILURE


def test_featurepack(featureexample, monkeypatch):
    root, path = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(worker), path)
        assert returncode(result) == SUCCESS


def returncode(exeception):
    return int(str(exeception.value))
