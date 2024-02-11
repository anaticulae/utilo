# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def file_line_length(path: str) -> int:
    """Count number of lines of given `path`.

    >>> file_line_length(__file__) >= 10
    True
    """
    return len(utila.file_read(path).splitlines())


def isfilepath(path: str) -> bool:
    """Check that given `path` is a file path.

    >>> isfilepath('/c/tmp/file.txt')
    True
    >>> isfilepath('/c/tmp/.tmp')
    False
    """
    assert path, path
    if os.path.exists(path):
        return os.path.isfile(path)
    base = os.path.basename(path)
    if base[0] == '.':
        # .tmp
        return False
    return '.' in base


def file_age(path: str) -> int:
    """Determine seconds since last file modification.

    >>> file_age(__file__) > 0
    True
    """
    filetime = os.stat(path).st_mtime
    timediff = utila.now() - filetime
    timediff = int(timediff)
    return timediff


def file_age_update(path: str, seconds: int = None) -> int:
    """Set seconds since last modification time."""
    assert os.path.exists(path), str(path)
    assert seconds >= 0 or seconds is None, str(seconds)
    if seconds is None:
        seconds = 0
    times = utila.now() - seconds
    os.utime(path, (times, times))


def file_size(path: str) -> float:
    """Return file size in MB.

    >>> file_size(__file__) > 0
    True
    """
    utila.exists_assert(path)
    status = os.stat(path)
    result = status.st_size
    # convert to MB
    result = result / 1000000
    return result


def path_parent(path: str) -> str:
    """\
    >>> path_parent(__file__)
    '.../utila/file'
    """
    parent = os.path.split(path)[0]
    parent = utila.forward_slash(parent, keep_newline=False)
    return parent


def path_current(path: str) -> str:
    """\
    >>> path_current(__file__)
    'info.py'
    """
    parent = os.path.split(path)[1]
    return parent
