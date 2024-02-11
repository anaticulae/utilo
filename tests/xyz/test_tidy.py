# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import utilatest

import utila.xyz.tidy

run = functools.partial(
    utilatest.run_cov,
    main=utila.xyz.tidy.main,
    process='utila_tidy',
    expect=True,
)
fail = functools.partial(
    utilatest.run_cov,
    main=utila.xyz.tidy.main,
    process='utila_tidy',
    expect=False,
)


def test_tidy_cli(testdir, mp, capsys):
    run('', mp=mp)
    stdout = utilatest.stdout(capsys)
    assert 'done' in stdout


EXAMPLE = utila.splitlines("""
astor-0.7.1-py2.py3-none-any.whl
argon2_cffi-20.1.0-cp37-cp37m-win32.whl
argon2_cffi-20.1.0-cp38-cp38-win_amd64.whl
pytest-6.2.4-py3-none-any.whl
pytest-bdd-3.4.0.tar.gz
pytest-konira-0.2.tar.gz
""")


def test_tidy_simple(testdir, mp, capsys):
    testdir.tmpdir.join('astor').mkdir()
    for package in EXAMPLE:
        utila.file_create(testdir.tmpdir.join(package))
    run('', mp=mp)
    stdout = utilatest.stdout(capsys)
    assert 'done' in stdout
    current = len(utila.directory_list(testdir.tmpdir))
    # Do not merge different pytest package into the same folder.
    assert current == 5


def test_tidy_twice(testdir, mp, capsys):
    testdir.tmpdir.join('astor').mkdir()
    for package in EXAMPLE:
        utila.file_create(testdir.tmpdir.join(package))
    run('', mp=mp)
    # create again to have double copy
    for package in EXAMPLE:
        utila.file_create(testdir.tmpdir.join(package))
    # run again
    run('', mp=mp)
    stdout = utilatest.stdout(capsys)
    assert 'done' in stdout
    current = len(utila.directory_list(testdir.tmpdir))
    # Do not merge different pytest package into the same folder.
    assert current == 5
    assert stdout.count('Skip package.') == len(EXAMPLE), stdout
