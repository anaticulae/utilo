#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import os
import typing

SUCCESS = 0
FAILURE = 1

TMP = '.tmp'
UTF8 = 'utf8'
NEWLINE = '\n'
INF = (1 << 31) - 1

ALL_PAGES = ':'


def flatten(lists):
    """Chain lists of list to one list"""
    result = []
    for item in lists:
        result.extend(item)
    return result


def select(items, selector) -> list:
    """Select items which are instance of `selector`

    >>> select([10, 'abc', 10.5], int)
    [10]
    >>> select([10, 'abc', 10.5], str)
    ['abc']
    >>> select([10, 'abc', 10.5], dict)
    []
    >>> select({'a':1, 'b':'zwei', 'c' : []}, list)
    [[]]

    Args:
        items(collection): data to filter
        selector(class): `type` of selected instance
    Returns:
        filtered collection which does not effect `items` collection
    """
    if isinstance(items, dict):
        items = items.values()
    selected = [item for item in items if isinstance(item, selector)]
    return selected


def determine_order(requirements, flat=True):
    requirements = dict(requirements)
    todo = list(requirements.keys())
    result = []
    while todo:
        level = []
        before = len(todo)
        for item in todo[:]:
            isparent = any([
                # check that item is not required by other resources
                current in todo or current in level
                for current in requirements[item]
            ])
            if isparent:
                continue
            todo.remove(item)
            level.append(item)
        # ensure that there is no multi option level
        level = sorted(level)
        result.append(level)
        assert len(todo) != before, 'cyclic definition of workplan'
    if flat:
        result = flatten(result)
    return result


@contextlib.contextmanager
def chdir(path: str) -> typing.NoReturn:
    """Contextmanager to change current working directory. Exceptions
    which where raised during accessing contextmanager are re-raised
    after changing current working directroy back to orgin.

    Args:
        path(str): path to change current working directory
    Yields:
        NoReturn: to run command in `path`
    Raises:
        Exception: if Exception occurrs while running contextmanager,
        the current working directory is changed back to location
        `before` and the occurred excetion is re raised after.
    Example:
        with utila.chdir(path):
            pass
    """
    assert os.path.exists(path) and not os.path.isfile(path), str(path)

    before = os.getcwd()

    os.chdir(path)
    try:
        yield
    except Exception:
        os.chdir(before)
        raise
    else:
        os.chdir(before)


@contextlib.contextmanager
def nothing(*args, **kwargs):  # pylint:disable=W0613
    """Use a empty contextmanager to ease code.

    Example:

        contextmanager = utila.profile if profiling else utila.nothing
        with contextmanager():
            pass
    """
    yield


def str2int(item: str) -> int:
    return int(float(item))


def str2bool(item: str) -> bool:
    """Convert string to bool. Every string except of `False` and
    `false` are converted to True.

    >>> str2bool('True')
    True
    >>> str2bool('False')
    False
    >>> str2bool('false')
    False
    >>> str2bool('Off')
    True
    >>> str2bool('abc')
    True
    """
    return not item.lower() == 'false'
