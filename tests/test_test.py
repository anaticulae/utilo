# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys
import webbrowser

import pytest

import utila
import utila.test
from utila import FAILURE
from utila import PACKAGENAME
from utila import ROOT
from utila import SUCCESS
from utila import assert_run
from utila import assert_run_fail
from utila import clean_install
from utila import run
from utila import run_command
from utila import skip_longrun


def test_run(tmpdir):
    completed = run('dir', tmpdir)
    assert completed.returncode == SUCCESS

    with assert_run('dir', tmpdir) as result:
        assert result.returncode == SUCCESS

    with assert_run_fail('this is not a command', tmpdir) as result:
        assert result.returncode == FAILURE


@skip_longrun
def test_clean_install():
    clean_install(ROOT, PACKAGENAME)


def test_test_run_command(monkeypatch):

    def main():
        # example runnable
        exit(SUCCESS)

    run_command('--number 10', 'main', main, True, monkeypatch)


def test_test_assert_success():
    completed = utila.run('python --help')
    utila.assert_success(completed)


def test_test_assert_success_failed():
    completed = utila.run('python --helpsambadamba', expect=None)
    with pytest.raises(AssertionError):
        utila.assert_success(completed)


def test_test_assert_failure():
    completed = utila.run('python --helpsambadamba', expect=None)
    utila.assert_failure(completed)


def test_test_assert_failure_failed():
    completed = utila.run('python --help')
    with pytest.raises(AssertionError):
        utila.assert_failure(completed)


def test_test_log_raw(capsys):
    content = 'Hello\nHello\nHello'

    with pytest.raises(AssertionError):
        assert len(content) > 1000, utila.log_raw(content)

    assert content in capsys.readouterr().out


def test_test_single_execution(monkeypatch):
    with monkeypatch.context() as context:
        context.setattr(sys, 'argv', ['-k', 'test_helm'])

        def test_helm():
            return utila.single_execution()

        result = test_helm()
    assert result, 'not a single test'


def test_test_increased_filecount(testdir):
    root = str(testdir)
    with utila.increased_filecount(root):
        utila.file_create('test.txt')


def test_test_increased_filecount_with_number(testdir):
    root = str(testdir)
    with utila.increased_filecount(root, diff=1):
        utila.file_create('test.txt')


def test_test_increased_filecount_with_ext(testdir):
    root = str(testdir)
    with pytest.raises(AssertionError):
        with utila.increased_filecount(root, ext='*.pdf'):
            utila.file_create('test_abc.txt')


def test_test_increased_filecount_to_few_created(testdir):
    root = str(testdir)
    with pytest.raises(AssertionError):
        with utila.increased_filecount(root):
            pass

    with pytest.raises(AssertionError):
        with utila.increased_filecount(root, diff=2):
            utila.file_create('test.txt')


def test_test_open_webbrowser(testdir, monkeypatch):
    # NOTE: don't know if that is a good test
    root = str(testdir)
    path = os.path.join(root, 'index.html')
    utila.file_create(path, 'Hello World')

    called = False

    def open_url(url, new=0, autoraise=True):  # pylint:disable=W0613
        nonlocal called
        called = True

    with monkeypatch.context() as context:
        context.setattr(utila.test, 'single_execution', lambda: True)
        context.setattr(webbrowser, 'open', open_url)
        with utila.open_webbrowser(path):
            pass
    assert called
