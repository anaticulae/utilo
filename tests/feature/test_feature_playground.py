# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Feature playground
==================

The feature playground eases to verify the cli commands of featurepack
implementation.

currently tested:

* --profile: log runtime of each working step
* --quite: suppress logging
"""

import contextlib
import os
import sys

import pytest

import utila
import utila.logger


def run_playground(
        cmd: str,
        main: dict,
        testdir,
        monkeypatch,
        capsys=None,
):
    """Setup working step with main(dict) which defines the passed
    parameter to featurepack(**main). `cmd` is passed as argv to run."""
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
    if capsys:
        stdout = capsys.readouterr().out
        stderr = capsys.readouterr().err
        return stdout, stderr
    return None


@pytest.mark.parametrize('cmd', ['', '--profile'])
def test_feature_playground_cli_profile(cmd, testdir, monkeypatch, capsys):
    """Print runtime for each working step."""
    stdout, _, = run_playground(
        cmd,
        {'profileflag': True},
        testdir,
        monkeypatch,
        capsys,
    )
    assert ('runtime(household):' in stdout) == bool(cmd)


@pytest.mark.parametrize('quite', ['', '--quite'])
def test_feature_playground_cli_quite(quite, testdir, monkeypatch, capsys):
    """Test to suppress logging when using --quite flag."""
    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'LEVEL', utila.logger.LEVEL_DEFAULT)
        cmd = f'--profile {quite}'
        stdout, _ = run_playground(
            cmd,
            {
                'profileflag': True,
                'quiteflag': True
            },
            testdir,
            monkeypatch,
            capsys,
        )
    assert bool(stdout) != bool(quite)


def test_feature_playground_pass_config_file(testdir, monkeypatch, capsys):
    """Test overwriting global flag in input parameter of working step."""
    config = str(os.path.join(testdir.tmpdir, 'config.cfg'))

    utila.file_create(
        config, """\
            # change global flag
            profile = True\n\n
            # change step input
            char_margin = 1234.5
        """)
    cmd = f'-c {config}'
    stdout, _, = run_playground(
        cmd,
        {},
        testdir,
        monkeypatch,
        capsys,
    )
    # parameter was passed
    assert '1234.5' in stdout, stdout
    # profiling was active
    assert ('runtime(household):' in stdout) == bool(cmd)


@pytest.mark.parametrize('flag', [True, False])
def test_feature_playground_pass_flag(flag, testdir, monkeypatch, capsys):
    cmd = '--sync' if flag else ''
    stdout, _, = run_playground(
        cmd,
        {},
        testdir,
        monkeypatch,
        capsys,
    )
    # parameter was passed
    if flag:
        assert 'True' in stdout, stdout
    else:
        assert 'False' in stdout, stdout
