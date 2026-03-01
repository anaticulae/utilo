# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import sys

import pytest

import utilo


def run_featurepack(
    cmd: str,
    main: dict,
    mp,
    exe=None,
    capsys=None,
    success: bool = True,
):
    """Setup working step with main(dict) which defines the passed
    parameter to featurepack(**main). `cmd` is passed as argv to run."""
    root = exe.ROOT
    with contextlib.suppress(AttributeError):
        cmd = cmd.split()
    cmd = [exe.PROCESS] + cmd
    with mp.context() as context:
        context.syspath_prepend(root)
        context.setattr(sys, 'argv', cmd)
        with pytest.raises(SystemExit) as result:
            exe.main(**main)
    verified = utilo.returncode(result) == utilo.SUCCESS
    assert verified == success, str(result)
    if capsys:
        stdout = capsys.readouterr().out
        stderr = capsys.readouterr().err
        return stdout, stderr
    return None
