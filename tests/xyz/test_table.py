# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import utilatest

import utilo
import utilo.xyz.table

DATA = """
FAR                     false alarm rate
FASTEM                                   Fast Emissivity Model
FASTEX                                   Fronts and Atlantic Storm Track Experiment
FDDA                    four-dimensional data assimilation
FEMA                                   Federal Emergency Management Agency
FFT                     fast Fourier transform
FGGE                                   First Global Atmospheric Research Program (GARP) Global Experiment
FGOALS-g1.0                                   Flexible Global Ocean–Atmosphere–Land System Model, gridpoint version 1.0 (source reference is for "g2," but similar)
FGOALS-s2                                   Flexible Global Ocean–Atmosphere–Land System Model, second spectral version
FIO-ESM                                   First Institute of Oceanography (FIO) Earth System Model (ESM)
FIRE                                   First International Satellite Cloud Climatology Project (ISCCP) Regional Experiment
FIRE-ACE                                   First International Satellite Cloud Climatology Project (ISCCP) Regional Experiment-Arctic Cloud Experiment
"""

run = functools.partial(
    utilatest.run_cov,
    main=utilo.xyz.table.main,
    process='utilo_table',
    expect=True,
)
fail = functools.partial(
    utilatest.run_cov,
    main=utilo.xyz.table.main,
    process='utilo_table',
    expect=False,
)


def test_normalize_table(td, mp):
    todo = td.tmpdir.join('table.txt')
    utilo.file_create(todo, DATA)
    run(f'{todo}', mp=mp)
    better = utilo.file_read(todo)
    assert better != DATA


def test_table_invalid_input(mp):
    fail('INVALID', mp=mp)


def test_table_not_a_file(td, mp, capsys):
    fail(str(td.tmpdir), mp=mp)
    stderr = utilatest.stderr(capsys)
    assert 'not a file:' in stderr


SEPARATOR = """
A;B;C;D;E;F
G;H;I
J;K;L;M;N
O;P;Q;R;S;T
"""
EXPECTED = """\
A;     B;     C;     D;     E;     F
G;     H;     I
J;     K;     L;     M;     N
O;     P;     Q;     R;     S;     T
"""


def test_normalize_table_separator(td, mp):
    todo = td.tmpdir.join('separator.txt')
    utilo.file_create(todo, SEPARATOR)
    run(f'{todo} --separator=; --sort=-1 --spaces=5', mp=mp)
    better = utilo.file_read(todo)
    assert better != SEPARATOR
    assert better == EXPECTED
