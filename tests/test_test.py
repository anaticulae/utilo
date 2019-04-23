# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from utila import FAILURE
from utila import SUCCESS
from utila.test import assert_run
from utila.test import assert_run_fail
from utila.test import run


def test_run(tmpdir):
    completed = run('dir', tmpdir)
    assert completed.returncode == SUCCESS

    with assert_run('dir', tmpdir) as result:
        assert result.returncode == SUCCESS

    with assert_run_fail('this is not a command', tmpdir) as result:
        assert result.returncode == FAILURE
