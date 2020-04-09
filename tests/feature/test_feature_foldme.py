# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import tests.feature.runner
import utila


def run_foldme(
        cmd: str,
        main: dict,
        testdir,
        monkeypatch,
        capsys=None,
):
    import tests.examples.featurepack.foldme.morefeatures as exe

    # directory_input step resource
    testdir.mkdir('iamadirectory')

    result = tests.feature.runner.run_featurepack(
        cmd=cmd,
        main=main,
        testdir=testdir,
        monkeypatch=monkeypatch,
        exe=exe,
        capsys=capsys,
    )
    return result


def test_directory_asinput(testdir, monkeypatch):
    root = testdir.tmpdir
    run_foldme('--directory_input', {}, testdir, monkeypatch)

    written = os.path.join(root, 'foldme__directory_input_message.yaml')
    loaded = utila.file_read(written)
    assert loaded.endswith('iamadirectory'), loaded
