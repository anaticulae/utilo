#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import inspect
import math
import os
import typing

import utila

SUCCESS = 0
FAILURE = 1

TMP = '.tmp'
UTF8 = 'utf8'
U8 = UTF8
NEWLINE = '\n'
NL = NEWLINE
INF = (1 << 31) - 1

ALL_PAGES = ':'

# Hint: Do not add string
ITERABLE = (list, tuple, set)


def flat(lists, append: bool = False) -> list:
    """Chain lists of list to one list.

    Args:
        lists(iter): content to chain
        append(bool): if True do not raise TypeError if item is not iterable
    Returns:
        List of chained items
    Raises:
        TypeError: if append is False and item to chain is not iterable

    >>> flat(([1, 2, 3], 4, 'he'), append=True)
    [1, 2, 3, 4, 'h', 'e']
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


def iflat(lists, append: bool = False) -> 'yield':
    """Chain lists of list to one list.

    Args:
        lists(iter): content to chain
        append(bool): if True do not raise TypeError if item is not iterable
    Yields:
        List of chained items
    Raises:
        TypeError: if append is False and item to chain is not iterable

    >>> list(iflat(([1, 2, 3, 4], [6, 7, 8, 0])))
    [1, 2, 3, 4, 6, 7, 8, 0]
    >>> list(iflat(([1, 2, 3], 4, 'he'), append=True))
    [1, 2, 3, 4, 'h', 'e']
    >>> list(iflat(([1, 2, 3], 4, 'he')))
    Traceback (most recent call last):
        ...
    TypeError: 'int' object is not iterable
    """
    for group in lists:
        try:
            for item in group:
                yield item
        except TypeError:
            if append:
                yield group
            else:
                raise


def flatten_content(items: 'iamraw.PageContents') -> list:
    result = []
    for item in items:
        result.extend(item.content)
    return result


def minus(first, second):
    """\
    >>> minus([1, 2, 3, 4], [3, 4])
    [1, 2]
    >>> minus([3, 4], [5, 6])
    [3, 4]
    """
    result = first[:]
    for item in second:
        with contextlib.suppress(ValueError):  # item is not in list
            result.remove(item)
    return result


def select_type(items, selector, count: int = None) -> list:
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
        count(int): max number of selected items
    Returns:
        filtered collection which does not effect `items` collection
    """
    if isinstance(items, dict):
        items = items.values()
    selected = [item for item in items if isinstance(item, selector)]
    if selected and count:
        if count == 1:
            return selected[0]
        return selected[0:count]
    return selected


def determine_order(requirements, flats=True):
    requirements = dict(requirements)
    todo = list(requirements.keys())
    result = []
    while todo:
        level = []
        before = len(todo)
        for item in todo[:]:
            isparent = any(
                # check that item is not required by other resources
                current in todo or current in level
                for current in requirements[item])
            if isparent:
                continue
            todo.remove(item)
            level.append(item)
        # ensure that there is no multi option level
        level = sorted(level)
        result.append(level)
        assert len(todo) != before, 'cyclic definition of workplan'
    if flats:
        result = flat(result)
    return result


@contextlib.contextmanager
def chdir(path: str) -> typing.NoReturn:
    """Contextmanager to change current working directory. Exceptions
    which where raised during accessing contextmanager are re-raised
    after changing current working directory back to origin.

    Args:
        path(str): path to change current working directory
    Yields:
        NoReturn: to run command in `path`
    Raises:
        Exception: if Exception occurs while running contextmanager,
        the current working directory is changed back to location
        `before` and the occurred exception is re raised after.
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
    """Use empty contextmanager to ease code.

    Example:
    >>> import utila
    >>> profiling = False
    >>> contextmanager = utila.profile if profiling else utila.nothing
    >>> with contextmanager():
    ...     pass
    """
    yield


def notnone(items):
    """\
    >>> notnone([1, 2, None, 0, '', 4, None])
    [1, 2, 0, '', 4]
    >>> notnone({'first': None, 'second': 0, 'third': 'hello'})
    {'second': 0, 'third': 'hello'}
    """
    if isinstance(items, dict):
        items = {
            key: value for key, value in items.items() if value is not None
        }
        return items
    return [item for item in items if item is not None]


def notempty(items):
    """Remove None, [] and '' out of `items`.

    >>> notempty(['', 0, 'items', None])
    [0, 'items']
    """
    return [item for item in items if item or item == 0]  # pylint:disable=C2001


def removekeys(items: dict, keys: set) -> dict:
    """\
    >>> removekeys({'first': None, 'second': 0, 'third': 'hello'}, keys=['third'])
    {'first': None, 'second': 0}
    """
    items = {key: value for key, value in items.items() if key not in keys}
    return items


@contextlib.contextmanager
def unset_env(
    var: str,
    skip: bool = True,
):
    """Temporary disable environment variable.

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
            # restore environmental variable
            os.environ[var] = before
        raise error
    else:
        if before is not None:
            os.environ[var] = before


def ifnone(value, *, default):
    """\
    >>> ifnone(None, default=10)
    10
    >>> ifnone(0, default=5)
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


def selbstwirksamkeit(func=None, *, usenone=False) -> callable:
    """Let decorator decide which data should be passed to the function."""

    def decorator(user_func):

        def wrapper(*args, **kwds):  # pylint:disable=W0613
            data = args[0]
            sig = inspect.signature(user_func)
            required = sig.parameters.keys()
            collected = collect_data(data, required, usenone)
            return user_func(*collected)

        return wrapper

    # support @decorator() and @decorator
    if func is None:
        return decorator
    return decorator(func)


def collect_data(data, required, usenone) -> list:
    # TODO: WE HAVE TO EXTEND THIS ACCESS LATER
    if isinstance(data, tuple):
        given = data._fields  # pylint:disable=W0212
        if usenone:
            access = lambda x: getattr(data, x, None)
        else:
            access = lambda x: getattr(data, x)
    else:
        given = data.keys()
        if usenone:
            access = lambda x: data.get(x, None)
        else:
            access = data.get
    try:
        collected = [access(name) for name in required]
    except AttributeError as error:
        msg = (f'attribute of defined function {required} is not '
               f'provided by data {given}')
        raise AttributeError(msg) from error
    return collected


def iterable(items) -> bool:
    """\
    >>> iterable((1, 2, 3))
    True
    >>> iterable('Helmut')
    False
    >>> iterable({5, 5, 5, 6})
    True
    """
    if isinstance(items, ITERABLE):
        return True
    return False


def ensure_tuple(items, skipnone: bool = True) -> bool:
    """\
    >>> ensure_tuple([1, 2, 3])
    (1, 2, 3)
    >>> ensure_tuple(1)
    (1,)
    >>> assert ensure_tuple(None) is None
    """
    if not isinstance(items, tuple):
        if skipnone and items is None:
            return None
        items = tuple(items) if iterable(items) else (items,)
    return items


def ensure_list(items, skipnone: bool = True) -> bool:
    """\
    >>> ensure_list((1, 2, 3))
    [1, 2, 3]
    >>> ensure_list(1)
    [1]
    >>> assert ensure_list(None) is None
    """
    if not isinstance(items, list):
        if skipnone and items is None:
            return None
        items = list(items) if iterable(items) else [items]
    return items


def rate_rel(first, second):
    """\
    >>> rate_rel((1, 2, 3), (1, 2, 3, 4, 5))
    0.6
    >>> rate_rel(5, 10)
    0.5
    """
    if not second:
        return 0.0
    try:
        rate = len(first) / len(second)
    except TypeError:
        rate = first / second
    rate = utila.roundme(rate, digits=3)
    return rate


def rate_sum(first, second):
    """\
    >>> rate_sum((1, 2, 3), (1, 2, 3, 4, 5))
    0.375
    >>> rate_sum(5, 10)
    0.333
    """
    if not second:
        return 0.0
    try:
        rate = len(first) / (len(second) + len(first))
    except TypeError:
        rate = first / (first + second)
    rate = utila.roundme(rate, digits=3)
    return rate


def pagebox_hash(page=None, box=None) -> int:
    """\
    >>> pagebox_hash(page=5, box=(10.5, 10.5, 20.5, 200.51))
    90015000105000105000205020051
    >>> pagebox_hash(page=-1, box=(-1.13, 54.68, 494.59, 422.15))
    90011000113005468049459042215
    """
    page = int(math.fabs(page))
    box = box if box else (0, 0, 0, 0)
    result = '9'
    result += str(page + 10).zfill(4)
    for item in box:
        item = math.fabs(item)
        item = str(item).replace('.', '')
        item = item.zfill(6)
        result += item
    result: str = int(result)
    return result


def testing() -> bool:
    """Determine if environment is exectued in test mode."""
    if os.environ.get('PYTEST_CURRENT_TEST', None):
        return True
    return False
