# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import time


def today(sortable: bool = True) -> str:
    """Determine date in `German` format.

    Args:
        sortable(bool): if True, use (year, month, day)
    Returns:
        Date of today in YYYY:MM:DD

    >>> today(False)
    '...'
    """
    cur = time.localtime(time.time())
    if sortable:
        return "%04d.%02d.%02d" % (cur.tm_year, cur.tm_mon, cur.tm_mday)  # pylint:disable=C0209
    return "%02d.%02d.%04d" % (cur.tm_mday, cur.tm_mon, cur.tm_year)  # pylint:disable=C0209


def current(seconds: bool = False) -> str:
    """Determine time in `German` format."""
    cur = time.localtime(time.time())
    if seconds:
        return "%02d:%02d:%02d" % (cur.tm_hour, cur.tm_min, cur.tm_sec)  # pylint:disable=C0209
    return "%02d:%02d" % (cur.tm_hour, cur.tm_min)  # pylint:disable=C0209


def timedate(sortable: bool = True) -> str:
    """Determine date in `German` format.

    Args:
        sortable(bool): if True, use (year, month, day)
    Returns:
        Date of and time today in YYYY:MM:DD hh:mm:ss

    >>> timedate(False)
    '...'
    """
    if sortable:
        return f'{today(sortable)} {current()}'
    return f'{current()} {today(sortable)}'


def filetime():
    """\
    >>> len(filetime())==15
    True
    """
    cur = time.localtime(time.time())
    day = "%04d%02d%02d" % (cur.tm_year, cur.tm_mon, cur.tm_mday)  # pylint:disable=C0209
    times = "%02d%02d%02d" % (cur.tm_hour, cur.tm_min, cur.tm_sec)  # pylint:disable=C0209
    result = f'{day}_{times}'
    return result


def now():
    result = int(time.time())
    return result
