#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from contextlib import contextmanager
from os import environ
from os.path import exists
from os.path import isdir
from subprocess import PIPE
from subprocess import run as _run

import pytest

VIRTUAL_ENV_KEY = 'VIRTUAL'

skip_not_virtual = pytest.mark.skipif(
    VIRTUAL_ENV_KEY not in environ, reason="Require virtual environment")

def run(command: str, cwd: str):
    """Run external process"""
    assert exists(cwd)
    msg = 'cwd %s is not a valid directory' % cwd
    assert isdir(cwd), msg
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
