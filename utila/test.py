#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import sys
from contextlib import contextmanager
from contextlib import suppress
from subprocess import PIPE
from subprocess import CompletedProcess
from subprocess import run as _run

from pytest import mark
from pytest import raises

from utila.utils import SUCCESS

VIRTUAL_ENV_KEY = 'VIRTUAL'
NON_VIRTUAL = VIRTUAL_ENV_KEY not in os.environ

FAST = 'FAST' in os.environ.keys()
LONGRUN = 'LONGRUN' in os.environ.keys()
FAST_TESTS = not LONGRUN or FAST

LONGRUN_REASON = 'test requires to mutch time'
VIRTUAL_REASON = 'requires virtual environmnet'
# pylint: disable=invalid-name
skip_longrun = mark.skipif(FAST_TESTS, reason=LONGRUN_REASON)
skip_nonvirtual = mark.skipif(NON_VIRTUAL, reason=VIRTUAL_REASON)


def run(command: str, cwd: str = None, env: dict = None) -> CompletedProcess:
    """Run external process

    Args:
        command(str/[str]): command to run
        cwd(str): current working directory
        env(dict): modify environment variable for test run. If nothing is
                   passed, the global environment variable is used.
    Returns:
        return completed process
    """
    cwd = cwd if cwd else os.getcwd()
    assert os.path.exists(cwd)
    msg = 'cwd %s is not a valid directory' % cwd
    assert os.path.isdir(cwd), msg

    env = os.environ if env is None else env

    completed = _run(
        command,
        cwd=cwd,
        env=env,
        errors='replace',
        shell=True,
        stderr=PIPE,
        stdout=PIPE,
        universal_newlines=True,
    )
    return completed


def run_command(
        command,
        process: str,
        main: callable,
        success: bool,
        monkeypatch,
):
    """Run `main` with `command`

    Args:
        command([str] or str): command to run
        process(str): name of executed tool
        main(callable): method to run
        success(bool): expectation that process succed or failes
        monkeypatch: pytest patch feature
    """
    with suppress(AttributeError):
        command = command.split()
    assert callable(main), str(main)

    with monkeypatch.context() as context:
        # proccess is removed as first arg
        context.setattr(sys, 'argv', [process] + command)
        with raises(SystemExit) as result:
            main()
    assert (returncode(result) == SUCCESS) == success, str(result)


@contextmanager
def assert_run(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode == SUCCESS, msg
    yield completed


@contextmanager
def assert_run_fail(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed


def clean_install(root, package):
    uninstall = 'pip uninstall %s -y' % package
    install = 'python setup.py install'

    clean_and_run = uninstall + ' && ' + install
    completed = run(clean_and_run, cwd=root)
    assert completed.returncode == SUCCESS, completed.stdout + completed.stderr


def install_and_run(root, package, executable=None):
    """Install and run --help to ensure basic function"""
    executable = executable if executable else package
    uninstall = 'pip uninstall %s -y' % package
    install = 'python setup.py install && %s --help' % executable

    clean_and_run = uninstall + ' && ' + install
    completed = run(clean_and_run, cwd=root)
    assert completed.returncode == SUCCESS, completed.stdout + completed.stderr


def returncode(exeception: Exception) -> int:
    """Determine returncode raised from exit()"""
    return int(str(exeception.value))
