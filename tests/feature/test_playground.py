# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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

import os

import pytest
import utilotest

import tests.feature.runner
import utilo
import utilo.logger


def run_playground(
    cmd: str,
    main: dict,
    td,
    mp,
    capsys=None,
):
    import tests.examples.featurepack.testfield.playground as exe  # pylint:disable=C0415
    utilo.file_create(os.path.join(str(td), 'infile.yaml'))
    result = tests.feature.runner.run_featurepack(
        cmd=cmd,
        main=main,
        mp=mp,
        exe=exe,
        capsys=capsys,
    )
    return result


@pytest.mark.parametrize('cmd', ['', '--profile'])
@utilotest.longrun
def test_feature_playground_cli_profile(cmd, td, mp, capsys):
    """Print runtime for each working step."""
    stdout, _, = run_playground(
        f'{cmd} -VV' if cmd else cmd,
        {'profileflag': True},
        td,
        mp,
        capsys,
    )
    assert ('runtime(household):' in stdout) == bool(cmd)


@pytest.mark.parametrize('quite', ['', '--quite'])
@utilotest.longrun
def test_feature_playground_cli_quite(quite, td, mp, capsys):
    """Test to suppress logging when using --quite flag."""
    cmd = f'--profile {quite}'
    with utilo.level_tmp(utilo.LEVEL_DEFAULT):
        stdout = run_playground(
            cmd,
            {
                'profileflag': True,
                'quiteflag': True
            },
            td,
            mp,
            capsys,
        )[0]
    assert bool(stdout) != bool(quite)


def test_feature_playground_pass_config_file(td, mp, capsys):
    """Test overwriting global flag in input parameter of working step."""
    config = str(os.path.join(td.tmpdir, 'config.cfg'))

    utilo.file_create(
        config, """\
            # change global flag
            profile = True\n\n
            # change step input
            char_margin = 1234.5
        """)
    cmd = f'-c {config}'
    stdout, _, = run_playground(
        f'{cmd} -VV',
        {},
        td,
        mp,
        capsys,
    )
    # parameter was passed
    assert '1234.5' in stdout, stdout
    # profiling was active
    assert ('runtime(household):' in stdout) == bool(cmd)


@pytest.mark.parametrize('flag', [True, False])
@utilotest.longrun
def test_feature_playground_pass_flag(flag, td, mp, capsys):
    cmd = '--sync' if flag else ''
    stdout, _, = run_playground(
        cmd,
        {},
        td,
        mp,
        capsys,
    )
    # parameter was passed
    if flag:
        assert 'True' in stdout, stdout
    else:
        assert 'False' in stdout, stdout


def test_write_binary_data(td, mp):
    # test writing hex file
    run_playground('--binary', {}, td, mp)
    expected_path = os.path.join(td.tmpdir, 'testfield__binary_binary.hex')
    binary = utilo.file_read_binary(expected_path)
    assert binary == b'I Love Binaries.', binary


def test_write_list_of_tuple(td, mp):
    # test writing hex file
    run_playground('--multiple', {}, td, mp)

    expected = [
        'testfield__multiple_0_info.yaml',
        'testfield__multiple_0_binary.hex',
        'testfield__multiple_1_info.yaml',
        'testfield__multiple_1_binary.hex',
    ]
    expected = [os.path.join(td.tmpdir, item) for item in expected]
    for item in expected:
        assert os.path.exists(item), str(item)


def test_write_selective_datatype(td, mp):
    with utilotest.increased_filecount(td.tmpdir, mindiff=2, maxdiff=2):
        run_playground('--datatype', {}, td, mp)
    path = os.path.join(td.tmpdir, 'testfield__datatype_selected.txt')
    assert os.path.exists(path), path
    written = utilo.file_read(path)
    assert written == 'CONTENT', written


def test_write_selective_datatype_multi(td, mp):
    expected = [
        (b'first', 'testfield__datatype_multi_0.txt'),
        (b'second', 'testfield__datatype_multi_1.fdp'),
        (b'\x00\x11\x22', 'testfield__datatype_multi_2.png'),
    ]

    with utilotest.increased_filecount(td.tmpdir, mindiff=4, maxdiff=4):
        run_playground('--datatype_multi', {}, td, mp)

    for content, filename in expected:
        path = os.path.join(td.tmpdir, filename)
        assert os.path.exists(path), path
        written = utilo.file_read_binary(path)
        assert written == content, written


@utilotest.longrun
def test_write_binary_data_disable(td, mp):
    # test writing hex file
    run_playground('--binary!', {}, td, mp)
    expected_path = os.path.join(td.tmpdir, 'testfield__binary_binary.hex')
    assert not os.path.exists(expected_path)


@utilotest.longrun
def test_write_binary_data_all_and_disable(td, mp):
    # test writing hex file
    with utilotest.increased_filecount(mindiff=3):
        run_playground('--binary! --all', {}, td, mp)
    expected_path = os.path.join(td.tmpdir, 'testfield__binary_binary.hex')
    assert not os.path.exists(expected_path)


def test_run_hashed_step(td, mp):
    with utilotest.increased_filecount(mindiff=3):
        run_playground('--hashed', {}, td, mp)

    current = utilo.file_list(td.tmpdir, include='bin')
    assert len(current) == 2

    expected_first = utilo.freehash(b'second')
    assert expected_first in current[0] or expected_first in current[1]
    expected_second = utilo.freehash(b'imageinfo')
    assert expected_second in current[1] or expected_second in current[0]


def test_run_hashed_multi_step(td, mp):
    with utilotest.increased_filecount(mindiff=6):
        run_playground('--hashed_multi', {}, td, mp)

    expected = set([
        b'info: yaml',
        b'content',
        b'second: yaml',
        b'second content',
        b'third yaml',
        b'third content',
    ])

    with utilo.chdir('testfield__hashed_multi_figures'):
        current = utilo.file_list('.')
        assert len(current) == len(expected)
        content = {utilo.file_read_binary(item) for item in current}
    assert content == expected


def test_run_hashed_list_ext(td, mp):
    with utilotest.increased_filecount(mindiff=3):
        run_playground('--hashed_list_ext', {}, td, mp)

    expected = set([
        b'content',
        b'second content',
        b'third content',
    ])

    with utilo.chdir('testfield__hashed_list_ext_figures'):
        current = utilo.file_list('.')
        assert len(current) == len(expected)
        content = {utilo.file_read_binary(item) for item in current}
    assert content == expected
