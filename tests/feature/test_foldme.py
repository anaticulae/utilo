# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utilotest

import tests.feature.runner
import utilo


def run_foldme(
    cmd: str,
    main: dict,
    td,
    mp,
    capsys=None,
    success: bool = True,
    create: bool = True,
):
    """Run `foldme` featurepackage.

    create: create default input data
    """
    import tests.examples.featurepack.foldme.morefeatures as exe  # pylint:disable=C0415
    if create:
        # directory_input step resource
        td.mkdir('iamadirectory')
    result = tests.feature.runner.run_featurepack(
        cmd=cmd,
        main=main,
        mp=mp,
        exe=exe,
        capsys=capsys,
        success=success,
    )
    return result


@utilotest.longrun
def test_directory_asinput(td, mp):
    root = td.tmpdir
    run_foldme('--directory_input', {}, td, mp)

    written = os.path.join(root, 'foldme__directory_input_message.yaml')
    loaded = utilo.file_read(written)
    assert loaded.endswith('iamadirectory'), loaded


@utilotest.longrun
def test_directory_asinput_missing_input(td, mp):
    # input directory does not exists
    run_foldme(
        '--directory_input',
        {},
        td,
        mp,
        create=False,
        success=True,
    )


@utilotest.longrun
def test_custom_output_folder_file(td, mp):
    # input directory does not exists
    run_foldme(
        '--custom_output',
        {},
        td,
        mp,
    )
    expected = os.path.join(td.tmpdir, 'helm/iamsounique.txt')
    assert os.path.exists(expected), str(expected)


@utilotest.longrun
def test_custom_output_folder_different_datatype(td, mp):
    # input directory does not exists
    run_foldme(
        '--different_datatype',
        {},
        td,
        mp,
    )
    for item in ('0.txt', '1.fdp', '2.png'):
        expected = os.path.join(td.tmpdir, f'schelm/{item}')
        assert os.path.exists(expected), str(expected)
