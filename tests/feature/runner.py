# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import sys

import pytest

import utila
import utila.logger


def run_featurepack(
        cmd: str,
        main: dict,
        testdir,
        monkeypatch,
        exe=None,
        capsys=None,
):
    """Setup working step with main(dict) which defines the passed
    parameter to featurepack(**main). `cmd` is passed as argv to run."""
    root = exe.ROOT

    with contextlib.suppress(AttributeError):
        cmd = cmd.split()
    cmd = [exe.PROCESS] + cmd
    with monkeypatch.context() as context:
        context.syspath_prepend(root)
        context.setattr(sys, 'argv', cmd)

        with pytest.raises(SystemExit) as result:
            exe.main(**main)

    assert utila.returncode(result) == utila.SUCCESS, str(result)
    if capsys:
        stdout = capsys.readouterr().out
        stderr = capsys.readouterr().err
        return stdout, stderr
    return None
