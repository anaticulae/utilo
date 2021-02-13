#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
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


def flatten(lists, append: bool = False) -> list:
    """Chain lists of list to one list.

    Args:
        lists(iter): content to chain
        append(bool): if True do not raise TypeError if item is not iterable
    Returns:
        List of chained items
    Raises:
        TypeError: if append is False and item to chain is not iterable
    """
    result = []
    for item in lists:
        try:
            result.extend(item)
        except TypeError:
            if append:
                result.append(item)
            else:
                raise
    return result


def flatten_content(items: 'iamraw.PageContents') -> list:
    result = []
    for item in items:
        result.extend(item.content)
    return result


def select_type(items, selector) -> list:
    """Select items which are instance of `selector`

    >>> select_type([10, 'abc', 10.5], int)
    [10]
    >>> select_type([10, 'abc', 10.5], str)
    ['abc']
    >>> select_type([10, 'abc', 10.5], dict)
    []
    >>> select_type({'a':1, 'b':'zwei', 'c' : []}, list)
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
    try:
        os.chdir(path)
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


def notnone(items):
    """\
    >>> notnone([1, 2, None, 0, '', 4, None])
    [1, 2, 0, '', 4]
    """
    return [item for item in items if item is not None]


def notempty(items):
    """Remove None, [] and '' out of `items`.

    >>> notempty(['', 0, 'items', None])
    [0, 'items']
    """
    return [item for item in items if item or item == 0]


@contextlib.contextmanager
def unset_env(
        var: str,
        skip: bool = True,
):
    """Temporary disable enviroment variable.

    Args:
        var(str): name to disable
        skip(bool): if True, do not raise KeyError if environment variable
                    does not exists
    Yields:
        None: if env var exists before or skip is True
    Raises:
        KeyError: if skip is False and env variable does not exists
        Exception: if user code does not work properly
    """
    # TODO: ADD MULTIPLE UNSET
    assert var, 'invalid environment variable'
    before = None
    if not skip and var not in os.environ:
        # TODO: not thread safe
        raise KeyError(f'missing env var: `{var}`')
    with contextlib.suppress(KeyError):
        before = os.environ[var]
    if before is not None:
        del os.environ[var]
    try:
        # run user code
        yield
    except Exception as error:
        if before is not None:
            # restore enviromental variable
            os.environ[var] = before
        raise error
    else:
        if before is not None:
            os.environ[var] = before


def ifnone(value, default):
    """\
    >>> ifnone(None, 10)
    10
    >>> ifnone(0, 5)
    0
    """
    return default if value is None else value


def index_max(*items):
    """\
    >>> index_max(2, 3, 3, 1)
    1
    >>> index_max(1, 2, 3, 4)
    3
    """
    if not items:
        return None
    best = 0
    for index, _ in enumerate(items[1:], start=1):
        best = best if items[best] >= items[index] else index
    return best
