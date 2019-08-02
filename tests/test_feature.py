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
from utila import file_read
from utila import parallelize_workplan
from utila import returncode
from utila.feature import Pattern
from utila.feature import ResultFile
from utila.feature import Value
from utila.feature import input_order

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
                ResultFile(producer='decider_border_hitthebox', name='hits'),
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
from utila import checkdatatype
@checkdatatype
def work(path : str) -> Tuple[str, str]:
    return 'work completed', 'Error'
    """)
    file_create('decider_border_hitthebox__hits.yaml', '')
    return root, featurepackage


# pylint:disable=W0621
def test_featurepack_without_input(featureexample, monkeypatch):
    """Running process without any args, runs all features in current working
    directory."""
    root, package = featureexample
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage=package)
        assert returncode(result) == SUCCESS


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
        assert returncode(result) == SUCCESS, str(result)


def create_worker(
        stepname: str,
        worker: str,
        featurepath: str,
):
    example = """
from utila import Flag

def name():
    return '{stepname}'

def commandline():
    return Flag(longcut='{stepname}', message='run {stepname}')

{worker}
"""

    example = example.format(stepname=stepname, worker=worker)
    outputpath = join(featurepath, '%s.py' % stepname)
    file_create(outputpath, example)


def create_example(
        root: str,
        featurepackage: str,
        stepname: str,
        worker: str,
):
    featurepath = join(root, featurepackage.replace('.', '/'))
    makedirs(featurepath)
    file_create(join(root, '__init__.py'))
    file_create(join(root, 'feedback/__init__.py'))
    file_create(join(root, 'feedback/features/__init__.py'))

    create_worker(stepname, worker, featurepath)


def test_feature_featurepack_workplan_pdf_parser(testdir, monkeypatch):
    """Test featurepack with multiple input via *.PDF"""
    # TODO: Clean up test creating process
    root = str(testdir)
    processname = 'pdfparser'
    featurepackage = 'feedback.features'
    featurepath = join(root, featurepackage.replace('.', '/'))
    stepname = 'parser'

    # Define first working step
    worker = """
def work(pdffile : str) -> str:
    return 'parsed_file'
"""
    workplan = [
        create_step(
            stepname,
            [
                Pattern('*', 'pdf'),
            ],
            (('result'),),
        ),
    ]
    examplepath = join(root, 'example')
    makedirs(examplepath)
    file_create(join(examplepath, 'test.pdf'), 'this pdf is empty')

    create_example(
        root,
        featurepackage=featurepackage,
        stepname=stepname,
        worker=worker,
    )

    # Define second work step
    path_with_value_worker =\
"""
def work(pdf : str, result: str, char_margin : float, char_align : float) -> str:
    return '%.2f %.2f' % (char_margin,char_align)
"""

    create_worker('path_with_value', path_with_value_worker, featurepath)
    workplan.append(
        create_step(
            'path_with_value',
            [
                Pattern('*', 'pdf'),
                ResultFile(producer=processname, name='result'),
                Value('char_margin', float, 0.1),
                Value('char_align', float, 20),
            ],
            (('result'),),
        ))

    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [
            processname,
            '-i',
            examplepath,
            '-o',
            root,
            '--char_margin',
            '1.0',
            '--char_align',
            '50.5',
        ])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            context.syspath_prepend(root)
            featurepack(
                workplan,
                root=root,
                featurepackage=featurepackage,
                name='parsi',
                description='Description',
                version='1.0.0',
                singleinput=True,
            )
    assert returncode(result) == SUCCESS
    written = file_read(join(root, 'parsi__path_with_value_result.yaml'))
    assert written == '1.00 50.50', str(written)


def test_feature_featurepack_help_with_variable(testdir, monkeypatch, capsys):
    # TODO: DIRTY CODE
    root = str(testdir)
    processname = 'pdfparser'
    featurepackage = 'feedback.features'
    featurepath = join(root, featurepackage.replace('.', '/'))

    path_with_value_worker = """
def work(pdf : str, result: str, char_margin : float, char_align : float) -> str:
    return '%.2f %.2f' % (char_margin,char_align)
"""
    makedirs(featurepath)

    # make directories to packages
    file_create(join(root, '__init__.py'), '')
    file_create(join(root, 'feedback/__init__.py'), '')
    file_create(join(root, 'feedback/features/__init__.py'), '')

    create_worker('path_with_value', path_with_value_worker, featurepath)
    workplan = [(create_step(
        'path_with_value',
        [
            Pattern('*', 'pdf'),
            ResultFile(producer=processname, name='result'),
            Value('char_margin', float, 0.1),
            Value('char_align', float, 20),
        ],
        (('result'),),
    ))]

    # check --help
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', [
            processname,
            '--help',
        ])
        context.syspath_prepend(root)
        with raises(SystemExit) as result:
            context.syspath_prepend(root)
            featurepack(
                workplan,
                root=root,
                featurepackage=featurepackage,
                name='parsi',
                description='Description',
                version='1.0.0',
                singleinput=True,
            )
    out, err = capsys.readouterr()
    assert not err, str(err)
    assert out.count('variable:') == 2, str(out)
    assert out.count('type:') == 2, str(out)
    assert out.count('default:') == 2, str(out)

    assert returncode(result) == SUCCESS


# TODO: REMOVE COPY AND PASTE, MOVE EXAMPLES TO REGULAR PYTHON FILES

PROCESS = 'process'
PLAN = [
    create_step(
        'second',
        [
            ResultFile(producer=PROCESS, name='third_result'),
            ResultFile(producer='first', name='b'),
            ResultFile(producer='B', name='c'),
        ],
        ('result',),
    ),
    create_step(
        'third',
        [
            ResultFile(producer=PROCESS, name='first_result'),
            ResultFile(producer=PROCESS, name='b_b'),
        ],
        ('result',),
    ),
    create_step(
        'first',
        [
            ResultFile(producer='A', name='a'),
            ResultFile(producer='A', name='b'),
            ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
]


def test_parallelize_workplan_order():
    # 2 level's
    order = input_order(PLAN)
    assert len(order) == 2, str(order)


def test_parallelize_workplan():
    # 3 level
    single_processed = parallelize_workplan(PLAN, 1)
    assert len(single_processed) == 3, str(single_processed)

    # multilevel limited by required resoure
    multi_processed = parallelize_workplan(PLAN, 10)
    assert len(multi_processed) == 2, str(multi_processed)
