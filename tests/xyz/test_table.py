# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import utilatest

import utila
import utila.xyz.table

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

TABLE = functools.partial(
    utilatest.run_command,
    main=utila.xyz.table.main,
    process='utila_table',
    success=True,
)


def test_normalize_table(testdir, monkeypatch):
    todo = testdir.tmpdir.join('table.txt')
    utila.file_create(todo, DATA)
    TABLE(f'{todo}', monkeypatch=monkeypatch)
    better = utila.file_read(todo)
    assert better != DATA
