# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
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
    for package in EXAMPLE:
        utila.file_create(testdir.tmpdir.join(package))
    run('', mp=mp)
    stdout = utilatest.stdout(capsys)
    assert 'done' in stdout
