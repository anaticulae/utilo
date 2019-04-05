#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from contextlib import contextmanager
from os import makedirs
from os.path import exists
from os.path import join
from random import randrange
from subprocess import PIPE
from subprocess import run as _run

import pytest
from utila.utils import TMP

skip_not_virtual = pytest.mark.skip(reason="Require virtual environment")

def tempname():
    """Get random file-name with 20-ziffre, random name

    Returns:
        filename(str): random file name
    """
    return str(randrange(MAX_TEST_RANDOM)).zfill(MAX_NUMBER)


def tempfile(project_root):
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert exists(project_root)
    TEMP = join(project_root, TMP)
    makedirs(TMP, exist_ok=True)

    name = 'temp%s' % tempname()
    path = join(TEMP, name)
    if exists(path):
        return tempfile()
    return path


def run(command: str, cwd: str):
    """Run external process"""
    completed = _run(
        command,
        cwd=cwd,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
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
