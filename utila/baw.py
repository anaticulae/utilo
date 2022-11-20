# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import os

import utila

BAW = '.baw'


def baw_root(path: str) -> str:
    """Go upwards till project config file occurs.

    >>> baw_root(__file__)
    '...'
    """
    current = str(path)
    while not utila.exists(utila.join(current, BAW)):  # pylint:disable=W0149
        current, base = os.path.split(current)
        if not str(base).strip():
            # root of file sytem
            return None
    return current


def baw_name(path: str) -> str:
    """\
    >>> baw_name(__file__)
    'utila'
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
    {'project': {'short': 'utila', 'name': 'write it once'},...'test': {'plugins': 'timeout'}}
    """
    root = baw_root(path)
    if not root:
        return None
    config = utila.join(root, BAW)
    result = utila.load_config(config)
    return result
