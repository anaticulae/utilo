#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import inspect
import os
import typing

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
    if flat:
        result = flatten(result)
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


def ensure_tuple(items) -> bool:
    """\
    >>> ensure_tuple([1, 2, 3])
    (1, 2, 3)
    """
    if not isinstance(items, tuple):
        items = tuple(items)
    return items


def ensure_list(items) -> bool:
    """\
    >>> ensure_list((1, 2, 3))
    [1, 2, 3]
    """
    if not isinstance(items, list):
        items = list(items)
    return items
