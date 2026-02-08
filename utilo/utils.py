#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import collections
import contextlib
import inspect
import math
import multiprocessing
import os
import subprocess
import sys
import threading
import typing

import utilo

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
    """\
    >>> import utila; flatten_content([utilo.driver(content=['Helmut'])])
    ['Helmut']
    """
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
    >>> select_type([10, 10, 9, 'abc', 10.5], int, count=2)
    [10, 10]
    >>> select_type([9, 10, 10, 9, 'abc', 10.5], int, count=1)
    9

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


def sfirst(item, convert=None):
    """\
    >>> sfirst('ABCDEF')
    'A'
    """
    return convert(item[0]) if convert else item[0]


def ssecond(item, convert=None):
    """\
    >>> ssecond('ABCDEF')
    'B'
    """
    return convert(item[1]) if convert else item[1]


def sthird(item, convert=None):
    """\
    >>> sthird('ABCDEF', convert=str.lower)
    'c'
    """
    return convert(item[2]) if convert else item[2]


def sattr(name: str, convert=None):
    """Select value by attribute name.

    >>> import utila
    >>> sorted((utilo.Command(shortcut='C'), utilo.Command(shortcut='Aello')), key=sattr('shortcut'))
    [Command(shortcut='Aello', longcut='', message='', args={}), Command(shortcut='C', longcut='', message='', args={})]
    """
    data = lambda x: getattr(x, name)  # pylint:disable=C3001
    return convert(data) if convert else data


def scall_or_me(selector=None, convert=None):
    """Use selector if given. If not, use value.

    Do not use any selector, use the value.
    >>> sorted((5,4,3,2,1), key=scall_or_me)
    [1, 2, 3, 4, 5]
    >>> sorted((5,4,3,2,1), key=scall_or_me(lambda x: -x))
    [5, 4, 3, 2, 1]
    """
    if selector:
        if convert:
            return lambda x: convert(selector(x))
        return selector
    return lambda x: convert(x) if convert else x  # pylint:disable=C3001


def sall_true(*args, **kwargs):  # pylint:disable=W0613
    """\
    >>> sall_true(False, False)
    True
    """
    return True


def sall_false(*args, **kwargs):  # pylint:disable=W0613
    """\
    >>> sall_false(True, False)
    False
    """
    return False


def sall_none(*args, **kwargs):  # pylint:disable=W0613
    """\
    >>> sall_none(True, False) is None
    True
    """
    return None


def determine_order(requirements, flats=True):
    """\
    >>> determine_order(dict(iamraw='utilo', hello='iamraw'))
    ['hello', 'iamraw']
    >>> determine_order(dict(hello='iamraw', iamraw='utilo'))
    ['hello', 'iamraw']
    >>> determine_order(dict())
    []
    """
    requirements = dict(requirements)
    todo = list(requirements.keys())
    result = []
    while todo:  # pylint:disable=W0149
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
        with utilo.chdir(path):
            pass
    """
    assert os.path.exists(path) and not os.path.isfile(path), str(path)
    before = utilo.cwdget()
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
    >>> contextmanager = utilo.profile if profiling else utilo.nothing
    >>> with contextmanager():
    ...     pass
    """
    yield


class Nothing(contextlib.ContextDecorator):

    def __enter__(self):
        pass

    def __exit__(self, *exc_info):
        pass


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

    >>> with unset_env('ABC_NO_VAR'):
    ...     raise ValueError('hello')
    Traceback (most recent call last):
    ...
    ValueError: hello
    >>> with unset_env('ABC_NO_VAR'):
    ...     pass
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
    >>> index_max() is None
    True
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
    """\
    >>> collect_data(dict(hello=10), ['hello'], False)
    [10]
    >>> collect_data(dict(hello=[10, 12]), ['hello'], False)
    [[10, 12]]
    >>> collect_data({}, [], True)
    []
    >>> collect_data({}, [], False)
    []
    """
    # TODO: WE HAVE TO EXTEND THIS ACCESS LATER
    if isinstance(data, tuple):
        given = data._fields  # pylint:disable=W0212
        if usenone:
            access = lambda x: getattr(data, x, None)  # pylint:disable=C3001
        else:
            access = lambda x: getattr(data, x)  # pylint:disable=C3001
    else:
        given = data.keys()
        if usenone:
            access = lambda x: data.get(x, None)  # pylint:disable=C3001
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
    >>> ensure_tuple((5,))
    (5,)
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
    >>> ensure_list([9])
    [9]
    """
    if not isinstance(items, list):
        if skipnone and items is None:
            return None
        items = list(items) if iterable(items) else [items]
    return items


def rate_rel(first, second) -> float:
    """\
    >>> rate_rel((1, 2, 3), (1, 2, 3, 4, 5))
    0.6
    >>> rate_rel(5, 10)
    0.5
    >>> rate_rel(1, 0)
    0.0
    """
    if not second:
        return 0.0
    try:
        rate = len(first) / len(second)
    except TypeError:
        rate = first / second
    rate = utilo.roundme(rate, digits=3)
    return rate


def rate_sum(first, second) -> float:
    """\
    >>> rate_sum((1, 2, 3), (1, 2, 3, 4, 5))
    0.375
    >>> rate_sum(5, 10)
    0.333
    >>> rate_sum(5, 0)
    0.0
    """
    if not second:
        return 0.0
    try:
        rate = len(first) / (len(second) + len(first))
    except TypeError:
        rate = first / (first + second)
    rate = utilo.roundme(rate, digits=3)
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
    """Determine if environment is exectued in test mode.

    >>> testing()
    True
    """
    if os.environ.get('PYTEST_CURRENT_TEST', None):
        return True
    if 'pytest' in sys.modules:
        return True
    return False


def driver(**kwargs):
    """\
    >>> driver(name='Helmut', age=33)
    Driver(name='Helmut', age=33)
    """
    Driver = collections.namedtuple('Driver', kwargs.keys())  # pylint:disable=C0103
    result = Driver(**kwargs)
    return result


def wait():
    """Ask user to continue program."""
    answer = input('continue?\n')
    answer = answer.strip().lower()
    if answer in {'no', 'n'}:
        utilo.exitx(returncode=utilo.SUCCESS)


def assert_unique(items):
    """\
    >>> assert_unique((1,2,3,4))
    >>> assert_unique((2,2,6,4))
    Traceback (most recent call last):
    ...
    ValueError: duplicate value: [2]
    """
    duplicated = []
    single = utilo.Single()
    for item in items:
        if single.contains(item):
            utilo.error(f'duplicated: {item}')
            duplicated.append(item)
    if duplicated:
        raise ValueError(f'duplicate value: {duplicated}')


def iswin() -> bool:
    """\
    >>> str(iswin())  # dependens on platform
    '...'
    """
    return 'win' in sys.platform


def ismainthread() -> bool:
    """\
    >>> str(ismainthread())
    '...'
    """
    if threading.current_thread() == threading.main_thread():
        return True
    return False


def mainthread() -> int:
    """Determine id of main_thread.

    >>> mainthread() > 0
    True
    """
    # TODO: REWORK THIS! THIS IS NOT REALY THE PROCESS ID
    key = multiprocessing.current_process()._config['authkey']  # pylint:disable=W0212
    process = utilo.binhash(key)
    return process


def isci() -> bool:
    """Is this a continous integration server?

    >>> str(isci())
    '...'
    """
    return os.environ.get('JENKINS_HOME', False)


def hasprog(program: str):
    """\
    >>> hasprog('utilo_lock')
    True
    >>> hasprog('superdupermagic')
    False
    """
    assert program, 'define program'
    check = 'where' if utilo.iswin() else 'which'
    completed = subprocess.run(  # pylint:disable=c2001 # nosec
        [check, program],
        check=False,
        capture_output=True,
    )
    installed = completed.returncode == utilo.SUCCESS
    if installed:
        expected = f'{program}:'
        if completed.stdout.strip() in {expected, expected.encode('utf8')}:
            # workaround for `whereis` of arch
            installed = False
    return installed


def cwdget():
    """\
    >>> str(cwdget())
    '...'
    """
    return os.getcwd()
