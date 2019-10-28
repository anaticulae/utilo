#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import os

SUCCESS = 0
FAILURE = 1

TMP = '.tmp'
UTF8 = 'utf8'
NEWLINE = '\n'
INF = (1 << 31) - 1

NDIGITS = 2

ALL_PAGES = ':'


def roundme(value: float, digits: int = NDIGITS) -> float:
    """Round `value` to `NDIGITS`=2

    Args:
        value(float): value to round
        digits(int): amout of numbers after dot
    Returns:
        rounded `value`
    """
    return round(value, digits)


def flatten(lists):
    """Chain lists of list to one list"""
    result = []
    for item in lists:
        result.extend(item)
    return result


def select(items, selector):
    """Select items which are instance of `selector`

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


def numbers(items):
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            result.append(None)
    return result


@contextlib.contextmanager
def chdir(path: str):
    """Contextmanager to change current working directory. Exceptions
    which where raised during accessing contextmanager are re-raised after
    changing current working directroy back to orgin.

    Args:
        path(str): path to change current working directory

    Example:
        with utila.chdir(path):
            pass
    """
    assert os.path.exists(path), str(path)

    before = os.getcwd()

    os.chdir(path)
    try:
        yield
    except Exception:
        os.chdir(before)
        raise
    else:
        os.chdir(before)
