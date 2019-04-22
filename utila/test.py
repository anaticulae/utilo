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
from os import makedirs
from os.path import exists
from os.path import isdir
from os.path import join
from random import randrange
from subprocess import PIPE
from subprocess import run as _run

import pytest
from utila.utils import TMP

VIRTUAL_ENV_KEY = 'VIRTUAL'

skip_not_virtual = pytest.mark.skipif(
    VIRTUAL_ENV_KEY not in environ, reason="Require virtual environment")

MAX_NUMBER = 20


def tempname(width: int = MAX_NUMBER) -> str:
    """Get random file-name with 20-ziffre, random name

    Args:
        width(int): length of tempname
    Returns:
        filename(str): random file name
    """
    assert width
    max_test_number = 10**width

    return str(randrange(max_test_number)).zfill(width)


def tempfile(project_root):
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert exists(project_root)
    tmp = join(project_root, TMP)
    makedirs(tmp, exist_ok=True)

    name = 'temp%s' % tempname()
    path = join(tmp, name)
    if exists(path):
        return tempfile(project_root)
    return path


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
