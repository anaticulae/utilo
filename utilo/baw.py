# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import os

import utilo

BAW = '.baw'


def baw_root(path: str, fail: bool = False) -> str:
    """Go upwards till project config file occurs.

    >>> baw_root(__file__)
    '...'
    >>> baw_root('/does/not/exists/', fail=True)
    Traceback (most recent call last):
    ...
    SystemExit: 1
    >>> baw_root('/does/not/exists/', fail=False) is None
    True
    """
    current = str(path)
    while not utilo.exists(utilo.join(current, BAW)):
        current, base = os.path.split(current)
        if not str(base).strip():
            # root of file sytem
            if fail:
                utilo.exitx('could not determine .baw file')
            return None
    return current


def baw_name(path: str) -> str:
    """\
    >>> baw_name(__file__)
    'utilo'
    """
    config = baw_config(path)
    if not config:
        return None
    return config.get('project').get('short')


def baw_desc(path: str) -> str:
    """\
    >>> baw_desc(__file__)
    'write it once'
    """
    config = baw_config(path)
    if not config:
        return None
    return config.get('project').get('name')


@functools.lru_cache
def baw_config(path: str) -> dict:
    """\
    >>> baw_config(__file__)
    {'project': {'short': 'utilo', 'name': 'write it once'}}
    """
    root = baw_root(path)
    if not root:
        return None
    config = utilo.join(root, BAW)
    result = utilo.load_config(config)
    return result
