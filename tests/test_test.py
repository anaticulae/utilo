# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from os.path import exists

from utila import FAILURE
from utila import SUCCESS
from utila.test import assert_run
from utila.test import assert_run_fail
from utila.test import run
from utila.test import tempfile
from utila.test import tempname


def test_tempname():
    name = tempname(width=15)
    assert len(name) == 15, name

    name = tempname(width=20)
    assert len(name) == 20, name


def test_tempfile(tmpdir):
    random_path = tempfile(tmpdir)

    assert not exists(random_path), random_path


def test_run(tmpdir):
    completed = run('dir', tmpdir)
    assert completed.returncode == SUCCESS

    with assert_run('dir', tmpdir) as result:
        assert result.returncode == SUCCESS

    with assert_run_fail('this is not a command', tmpdir) as result:
        assert result.returncode == FAILURE
