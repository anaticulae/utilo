# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import pytest
import utilotest

import utilo
from utilo import FAILURE
from utilo import SUCCESS
from utilo import FeaturePackConfig
from utilo import Pattern
from utilo import ResultFile
from utilo import Value
from utilo import create_step
from utilo import featurepack
from utilo import file_create
from utilo import file_read
from utilo import returncode

WORKER = """
from typing import Tuple
def work(input_with_pag: str, pages: list) -> Tuple[str, str]:
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
    config = FeaturePackConfig(
        description=description,
        name=PROCESS_NAME,
        version=version,
    )
    executed = featurepack(
        config=config,
        featurepackage=featurepackage,
        root=root,
        workplan=plan,
    )
    return executed


@pytest.fixture
def featureexample(td):
    root = str(td)
    featurepackage = 'feedback.features.border'
    feature_path = os.path.join(root, featurepackage.replace('.', '/'))
    os.makedirs(feature_path)
    file_create(os.path.join(root, '__init__.py'))
    file_create(os.path.join(root, 'feedback/__init__.py'))
    file_create(os.path.join(root, 'feedback/features/__init__.py'))
    file_create(os.path.join(feature_path, '__init__.py'))

    file_create(os.path.join(feature_path, 'incomplete_worker.py'), """
def work():
    return 'work'
    """)
    file_create(
        os.path.join(feature_path, 'complete_worker.py'), """
from utilo import Flag
def name():
    return 'complete_worker'
def commandline():
    return Flag(longcut=name(), message='export the html result of %s' % name())
from typing import Tuple
from utilo import checkdatatype
@checkdatatype
def work(path : str) -> Tuple[str, str]:
    return 'work completed', 'Error'
    """)
    file_create('decider_border_hitthebox__hits.yaml', '')
    return root, featurepackage


# pylint:disable=W0621
def test_featurepack_without_input(featureexample, mp):
    """Running process without any args, runs all features in current working
    directory."""
    root, package = featureexample
    with mp.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME])
        context.syspath_prepend(root)
        with pytest.raises(SystemExit) as result:
            pack(workplan() * 2, root=root, featurepackage=package)
        assert returncode(result) == SUCCESS


def test_featurepack_with_broken_feature(featureexample, mp):
    """Skip broken worker"""
    root, package = featureexample
    # create the broken feature
    file_create(os.path.join(package.replace('.', '/'), 'broken_worker.py'))

    with mp.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with pytest.raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage=package)
        assert returncode(result) == FAILURE


@pytest.mark.parametrize(
    'name,worker,expected_result',
    [
        ('worker_with_exception', WORKER_WITH_EXCEPTION, FAILURE),
        ('worker_with_no_returnvalue', WORKER_WITH_NO_RETURNVALUE, FAILURE),
        ('worker_with_wrong_input', WORKER_WITH_WRONG_INPUT, FAILURE),
        ('worker_with_wrong_returnval', WORKER_WITH_WRONG_RETURNVALUE, FAILURE),
        ('worker_with_pages', WORKER, SUCCESS),
    ],
    ids=[
        'worker_with_expection',
        'worker_with_no_returnvalue',
        'worker_with_wrong_input',
        'worker_with_wrong_returnvalue',
        'worker_with_pages',
    ],
)
@utilotest.longrun
def test_featurepack_with_different_worker(  #pylint:disable=W0621
        featureexample,
        mp,
        name,
        worker,
        expected_result,
):
    root, package = featureexample
    featurepath = os.path.join(root, package.replace('.', '/'))
    # create feature
    file_create(os.path.join(
        featurepath,
        f'{name}.py',
    ), worker)
    with mp.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)

        with pytest.raises(SystemExit) as result:
            pack(workplan(name) * 3, root=root, featurepackage=package)
        assert returncode(result) == expected_result, str(result)


def test_featurepack(featureexample, mp):  #pylint:disable=W0621
    root, package = featureexample
    with mp.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with pytest.raises(SystemExit) as result:
            pack(workplan() * 2, root=root, featurepackage=package)
        assert returncode(result) == SUCCESS, str(result)


def test_featurepack_wrong_featurepath(featureexample, mp, capsys):  #pylint:disable=W0621
    root, _ = featureexample
    with mp.context() as context:
        context.setattr(sys, 'argv', [PROCESS_NAME, '-i', root, '-o', root])
        context.syspath_prepend(root)
        with pytest.raises(SystemExit) as result:
            pack(workplan(), root=root, featurepackage='features.wrongpath')
        assert returncode(result) == FAILURE, str(result)
        err = utilotest.stderr(capsys)
        expected = '[ERROR] wrong featurepack configuration,\n check'
        assert expected in err, err


def create_worker(
    stepname: str,
    worker: str,
    featurepath: str,
):
    example = """
from utilo import Flag

def name():
    return '{stepname}'

def commandline():
    return Flag(longcut='{stepname}', message='run {stepname}')

{worker}
"""

    example = example.format(stepname=stepname, worker=worker)
    outputpath = os.path.join(featurepath, f'{stepname}.py')
    file_create(outputpath, example)


def create_example(
    root: str,
    featurepackage: str,
    stepname: str,
    worker: str,
):
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
    os.makedirs(featurepath)
    file_create(os.path.join(root, '__init__.py'))
    file_create(os.path.join(root, 'feedback/__init__.py'))
    file_create(os.path.join(root, 'feedback/features/__init__.py'))

    create_worker(stepname, worker, featurepath)


@utilotest.longrun
def test_feature_featurepack_workplan_pdf_parser(td, mp):
    """Test featurepack with multiple input via `*.PDF`

    Create worker which detect resource by *.PDF-Filepattern and accept
    some parameter for configuration.

    Worker structure:
        - parser(*.pdf)
        - path_with_value(*.pdf, pdfparser_result, char_margin, char_align)

    TODO: This example is very dirty and must be reworked.
    """
    root = str(td)
    processname = 'pdfparser'
    featurepackage = 'feedback.features'
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
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
    examplepath = os.path.join(root, 'example')
    os.makedirs(examplepath)
    file_create(os.path.join(examplepath, 'test.pdf'), 'this pdf is empty')

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

    with mp.context() as context:
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
        config = FeaturePackConfig(
            description='Description',
            name='parsi',
            singleinput=True,
            version='1.0.0',
        )
        with pytest.raises(SystemExit) as result:
            context.syspath_prepend(root)
            featurepack(
                config=config,
                featurepackage=featurepackage,
                root=root,
                workplan=workplan,
            )
    assert returncode(result) == SUCCESS
    written = file_read(os.path.join(root, 'parsi__path_with_value_result.yaml')) # yapf:disable
    assert written == '1.00 50.50', str(written)


@utilotest.longrun
def test_feature_featurepack_help_with_variable(td, mp, capsys):
    # TODO: DIRTY CODE
    root = str(td)
    processname = 'pdfparser'
    featurepackage = 'feedback.features'
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))

    path_with_value_worker = """
def work(pdf : str, result: str, char_margin : float, char_align : float) -> str:
    return '%.2f %.2f' % (char_margin,char_align)
"""
    os.makedirs(featurepath)

    # make directories to packages
    file_create(os.path.join(root, '__init__.py'), '')
    file_create(os.path.join(root, 'feedback/__init__.py'), '')
    file_create(os.path.join(root, 'feedback/features/__init__.py'), '')

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
    with mp.context() as context:
        context.setattr(sys, 'argv', [
            processname,
            '--help',
        ])
        context.syspath_prepend(root)
        config = FeaturePackConfig(
            name='parsi',
            description='Description',
            version='1.0.0',
            singleinput=True,
        )
        with pytest.raises(SystemExit) as result:
            context.syspath_prepend(root)
            featurepack(
                config=config,
                featurepackage=featurepackage,
                root=root,
                workplan=workplan,
            )
    out, err = capsys.readouterr()
    assert not err, str(err)
    assert 'char_align(float)=20' in out
    assert 'char_margin(float)=0.1' in out

    assert returncode(result) == SUCCESS


@pytest.mark.parametrize('hook, failfast', [
    (True, False),
    (True, True),
    (False, False),
    (False, True),
])
@utilotest.longrun
def test_error_hook(hook, failfast, td, mp):
    """Test passing exception to error hook and without hook"""
    import tests.examples.featurepack.withexception.withexception as exe  # pylint:disable=C0415
    root = exe.ROOT
    utilo.file_create(os.path.join(str(td), 'inputso.yaml'))

    def errorhook(name, exception):  # pylint:disable=W0613
        errorhook.hooked = True

    with mp.context() as context:
        context.syspath_prepend(root)
        if hook:
            context.setattr(exe, 'errorhook', errorhook)
        command = [exe.PROCESS]
        if failfast:
            command.append('--ff')
        context.setattr(sys, 'argv', command)

        with pytest.raises(SystemExit) as result:
            exe.main()

    assert utilo.returncode(result) == utilo.FAILURE
    assert not hook or errorhook.hooked


def test_featurepack_config_valid():

    def install(parser):  # pylint:disable=W0613
        pass

    def run(args):  # pylint:disable=W0613
        pass

    hook = install, run
    utilo.FeaturePackConfig(cli_hook=hook)


def test_featurepack_config_invalid():

    def install(parser):  # pylint:disable=W0613
        pass

    def run():  # pylint:disable=W0613
        pass

    hook = install, run
    with pytest.raises(AssertionError):
        utilo.FeaturePackConfig(cli_hook=hook)
