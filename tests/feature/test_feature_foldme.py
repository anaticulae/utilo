# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utilatest

import tests.feature.runner
import utila


def run_foldme(
        cmd: str,
        main: dict,
        testdir,
        monkeypatch,
        capsys=None,
        success: bool = True,
        create: bool = True,
):
    """Run `foldme` featurepackage.

    create: create default input data
    """
    import tests.examples.featurepack.foldme.morefeatures as exe

    if create:
        # directory_input step resource
        testdir.mkdir('iamadirectory')

    result = tests.feature.runner.run_featurepack(
        cmd=cmd,
        main=main,
        testdir=testdir,
        monkeypatch=monkeypatch,
        exe=exe,
        capsys=capsys,
        success=success,
    )
    return result


@utilatest.longrun
def test_directory_asinput(testdir, monkeypatch):
    root = testdir.tmpdir
    run_foldme('--directory_input', {}, testdir, monkeypatch)

    written = os.path.join(root, 'foldme__directory_input_message.yaml')
    loaded = utila.file_read(written)
    assert loaded.endswith('iamadirectory'), loaded


@utilatest.longrun
def test_directory_asinput_missing_input(testdir, monkeypatch):
    # input directory does not exists
    run_foldme(
        '--directory_input',
        {},
        testdir,
        monkeypatch,
        create=False,
        success=True,
    )


@utilatest.longrun
def test_custom_output_folder_file(testdir, monkeypatch):
    # input directory does not exists
    run_foldme(
        '--custom_output',
        {},
        testdir,
        monkeypatch,
    )
    expected = os.path.join(testdir.tmpdir, 'helm/iamsounique.txt')
    assert os.path.exists(expected), str(expected)


@utilatest.longrun
def test_custom_output_folder_different_datatype(testdir, monkeypatch):
    # input directory does not exists
    run_foldme(
        '--different_datatype',
        {},
        testdir,
        monkeypatch,
    )
    for item in ['0.txt', '1.fdp', '2.png']:
        expected = os.path.join(testdir.tmpdir, f'schelm/{item}')
        assert os.path.exists(expected), str(expected)
