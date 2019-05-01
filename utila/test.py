#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import sys
from contextlib import contextmanager
from contextlib import suppress
from subprocess import PIPE
from subprocess import run as _run

from pytest import mark
from pytest import raises

VIRTUAL_ENV_KEY = 'VIRTUAL'
NON_VIRTUAL = VIRTUAL_ENV_KEY not in os.environ

# pylint: disable=invalid-name
skip_nonvirtual = mark.skipif(NON_VIRTUAL, reason="Require virtual environment")
skip_not_virtual = skip_nonvirtual


def run(command: str, cwd: str = None):
    """Run external process"""
    cwd = cwd if cwd else os.getcwd()
    assert os.path.exists(cwd)
    msg = 'cwd %s is not a valid directory' % cwd
    assert os.path.isdir(cwd), msg
    completed = _run(
        command,
        cwd=cwd,
        errors='replace',
        shell=True,
        stderr=PIPE,
        stdout=PIPE,
        universal_newlines=True,
    )
    return completed


def run_command(command, monkeypatch, process, main, success=True):
    """Run `main` with `command`

    Args:
        command([str] or str): command to run
        monkeypatch: pytest patch feature
        process(str): name of executed tool
        main(callable): method to run
        success(bool): expectation that process succed or failes
    """
    with suppress(AttributeError):
        command = command.split()
    assert callable(main), str(main)

    with monkeypatch.context() as context:
        # proccess is removed as first arg
        context.setattr(sys, 'argv', [process] + command)
        with raises(SystemExit) as result:
            main()
        result = str(result)

    if success:
        assert 'SystemExit: 0' in result, result
    else:
        assert 'SystemExit: 1' in result, result


@contextmanager
def assert_run(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode == 0, msg
    yield completed


@contextmanager
def assert_run_fail(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed
