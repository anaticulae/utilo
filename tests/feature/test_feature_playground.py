# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import sys

import pytest

import utila


def run_playground(
        cmd,
        main,
        testdir,
        monkeypatch,
        capsys,
):
    import tests.examples.featurepack.testfield.playground as exe
    root = exe.ROOT
    utila.file_create(os.path.join(str(testdir), 'infile.yaml'))

    with contextlib.suppress(AttributeError):
        cmd = cmd.split()
    cmd = [exe.PROCESS] + cmd
    with monkeypatch.context() as context:
        context.syspath_prepend(root)
        context.setattr(sys, 'argv', cmd)

        with pytest.raises(SystemExit) as result:
            exe.main(**main)

    assert utila.returncode(result) == utila.SUCCESS
    stdout = capsys.readouterr().out
    stderr = capsys.readouterr().err
    return stdout, stderr


def test_feature_playground_cli(testdir, monkeypatch, capsys):
    cmd = '--profile'
    stdout, _, = run_playground(
        cmd,
        {'profilingflag': True},
        testdir,
        monkeypatch,
        capsys,
    )
    assert 'runtime(household):' in stdout
