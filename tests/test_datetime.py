# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from utilo import current
from utilo import timedate
from utilo import today


def test_today():
    assert len(today()) == 10
    assert today().count('.') == 2


def test_current():
    assert len(current()) == 5
    assert current().count(':') == 1

    assert len(current(True)) == 8
    assert current(True).count(':') == 2


def test_time_and_date():
    assert ' ' in timedate()
