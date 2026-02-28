# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import importlib.util
import inspect

import utilo


def checkdatatype(func) -> callable:
    """Decorator to ensure that passed data matches with defined datatype.

    Args:
        func(callable): function to ensure correct data input
    Returns:
        ensured callable
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        parameter = list(inspect.signature(func).parameters.items())
        parameter = [(name, item.annotation) for (name, item) in parameter]
        errors = []
        for current, (name, expected) in zip(args, parameter):
            if isinstance(current, expected):
                continue
            if expected is inspect.Signature.empty:
                continue
            msg = 'parameter: %s, expected: %r, current %r:'
            errors.append((msg % (name, expected, type(current))))
            errors.append(str(current))
        if errors:
            uf_name = func.__name__
            utilo.error(f'invalid function input `{uf_name}`')
            for item in errors:
                utilo.error(item)
            raise ValueError(f'invalid function input {uf_name}')
        return func(*args, **kwargs)

    return wrapper


Strings = list[str]


def isstrings(items) -> bool:
    """Ensure to have list of str.

    >>> isstrings(['hello', 'my', 'man'])
    True
    >>> isstrings('test')
    False
    >>> isstrings(10)
    False
    >>> isstrings({'hi': 'me'})
    False
    >>> isstrings(('H', 'B', 10))
    False
    >>> isstrings(None)
    False
    """
    if not utilo.iterable(items):
        return False
    return all((isinstance(item, str) for item in items))


def asserts_types(items, types):
    """Ensure that `items` is a list and the types of the single `items`
    matches width `types`.

    >>> asserts_types([1, 3, 5, 10], int)

    >>> asserts_types([1, 'hello', 10], str)  #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AssertionError: [False, True, False]
    """
    assert isinstance(items, (list, tuple)), type(items)
    verified = [isinstance(item, types) for item in items]
    assert all(verified), str(verified)


def isnumber(item: str) -> bool:
    """Check if `item` is a number.

    >>> isnumber('ten')
    False
    >>> isnumber(10.5)
    True
    >>> isnumber('3.5')
    True
    >>> isnumber(None)
    False
    """
    with contextlib.suppress(ValueError):
        _ = float(str(item))
        return True
    return False


def isint(item: str) -> bool:
    """Check if `item` is a int.

    >>> isint('ten')
    False
    >>> isint(10.5)
    False
    >>> isint('3')
    True
    >>> isint(0)
    True
    """
    with contextlib.suppress(ValueError):
        _ = int(str(item))
        return True
    return False


def equal_length(*items) -> bool:
    """\
    >>> equal_length([1, 2], (2,), [3, 3, 3])
    False
    >>> equal_length((1,), (2,))
    True
    >>> equal_length([3, 3, 3], [3, 3, 3])
    True
    """
    length = {len(item) for item in items}
    if len(length) > 1:
        return False
    return True


# TODO: add isbool method


def isfloat(*floats) -> bool:
    """\
    >>> isfloat(1.0)
    True
    >>> isfloat(1)
    False
    >>> isfloat(1.5, 'test')
    False
    >>> isfloat(1.5, 3.0, -0.3)
    True
    >>> isfloat('2.5')
    True
    """
    # TODO: RENAME TO isfloats
    return all(isfloat_(item) for item in floats)


def isfloat_(item) -> bool:
    """
    >>> isfloat_(1.0)
    True
    >>> isfloat_(0.0)
    True
    >>> isfloat_(-0.0)
    True
    >>> isfloat_('1.0')
    True
    >>> isfloat_('0')
    False
    """
    if (isinstance(item, float)):
        return True
    if (isinstance(item, str)):
        return '.' in item and isfloat_(float(item))
    return False


def asserts(item, typ):
    """\
    >>> asserts('hello', int)
    Traceback (most recent call last):
        ...
    AssertionError: require: <class 'int'>, got: <class 'str'>, raw:
    'hello'
    >>> asserts(10, int)
    """
    if isinstance(item, typ):
        return
    msg = f'require: {typ}, got: {type(item)}, raw:\n{item!r}'
    raise AssertionError(msg)


def hasattribute(caller, attribute) -> bool:
    """\
    >>> hasattribute(hasattribute, 'caller')
    True
    >>> hasattribute(hasattribute, 'false')
    False
    """
    parameters = attributes(caller)
    if attribute in parameters:
        return True
    return False


def attributes(method: callable, skipstars: bool = False) -> tuple:
    """\
    >>> attributes(attributes)
    ('method', 'skipstars')
    >>> attributes(isfloat)
    ('floats',)
    >>> attributes(isfloat, skipstars=True)
    ()
    """
    sig = inspect.signature(method)
    result = tuple(key for key, value in sig.parameters.items()
                   if '*' not in str(value) or not skipstars)
    return result


def annotations(method: callable, skipstars: bool = False) -> tuple:
    """\
    >>> annotations(attributes)
    (<built-in function callable>, <class 'bool'>)
    >>> annotations(isfloat)
    (<class 'inspect._empty'>,)
    >>> annotations(isfloat, skipstars=True)
    ()
    """
    sig = inspect.signature(method)
    result = (value.annotation
              for key, value in sig.parameters.items()
              if '*' not in str(value) or not skipstars)
    result = tuple(result)
    return result


def defaults(method: callable, skipstars: bool = False) -> tuple:
    """\
    >>> defaults(defaults)
    (<class 'inspect._empty'>, False)
    """
    sig = inspect.signature(method)
    result = (value.default
              for key, value in sig.parameters.items()
              if '*' not in str(value) or not skipstars)
    result = tuple(result)
    return result


def defaults_overwrite(func: callable) -> callable:
    """\
    >>> @defaults_overwrite
    ... def myfunc(a=1, b=True, c='off', overwrite: dict=None):
    ...     print(a, b, c)
    >>> myfunc(a=5, overwrite=dict(b=10, c='on'))
    5 10 on
    >>> myfunc(a=5, overwrite=dict(novalue=10))
    Traceback (most recent call last):
    ...
    ValueError: invalid `overwrite` config
    >>> myfunc()
    1 True off
    """
    assert 'overwrite' in attributes(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        parameters = attributes(func)
        if kwargs.get('overwrite', None):
            error = 0
            for key, value in kwargs['overwrite'].items():
                if key not in parameters:
                    utilo.error(f'no parameter: {key} in {func}')
                    error += 1
                    continue
                kwargs[key] = value
            if error:
                raise ValueError('invalid `overwrite` config')
        return func(*args, **kwargs)

    return wrapper


def methods(item, starts=''):
    """\
    >>> methods('', starts='zfi')
    [<built-in method zfill of str object at...>]
    >>> names = [item.__name__ for item in methods('')]

    Ensure that methods are not sorted
    >>> sorted(names)!= names
    True

    Regression that
    >>> methods('')
    [...<method-wrapper '__repr__'...<built-in method __dir__ of str object at 0x...>, <class 'str'>]
    """
    result = []
    # TODO: dir() and __dir__() is not the same, dir() sorts the keys
    # alphabetically.
    for name in item.__dir__():  # pylint:disable=C2801
        method = getattr(item, name)
        if not callable(method):
            continue
        if not name.startswith(starts):
            continue
        result.append(method)
    return result


def pass_required(caller: callable, default=None, **kwargs):
    """\
    >>> method = lambda alpha, beta: alpha + beta
    >>> pass_required(method, default=5, beta=20)
    25
    >>> def starpattern(first, second, *last):
    ...     '*last is not a keyword argument, skip stars'
    ...     print(first, second, last)
    >>> pass_required(caller=starpattern, last=30, first=10, second=20)
    10 20 ()
    """
    keys = attributes(caller, skipstars=True)
    data = {key: kwargs.get(key, default) for key in keys}
    result = caller(**data)
    return result


def load_module(path: str):
    """\
    >>> load_module(__file__).__name__
    'utilo.typechecker'
    >>> import utilo; load_module(utilo.ROOT)
    Traceback (most recent call last):
    ...
    ValueError: invalid spec in ...; parent: ...
    """
    item = utilo.file_name(path)
    parent = utilo.file_name(utilo.path_parent(path))
    spec = importlib.util.spec_from_file_location(
        f'{parent}.{item}',
        path,
    )
    if not spec:
        raise ValueError(f'invalid spec in {path}; parent: {parent}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rename(func: callable = None, **newnames):
    """\
    >>> @rename(old_a='a', old_b='b')
    ... def method(a:int=10, b:str='hello'):
    ...     print(a, b)
    >>> method(b=8, old_a=10)
        outdated interface: old_a => a
    10 8
    >>> method(b=8, a=10) # print warning only once
    10 8
    >>> method(b=8, old_a=10)
    10 8
    >>> method(old_b=8, old_a=10)
        outdated interface: old_b => b
    10 8
    """
    assert func is None

    def change_args(func):
        interface = attributes(func)

        def wrapper(*args, **kwargs):
            renames = {}
            for key, value in kwargs.items():
                if key in interface:
                    renames[key] = value
                    continue
                utilo.warning(f'outdated interface: {key} => {newnames[key]}')
                renames[newnames[key]] = value
            updated = functools.partial(func, *args, **renames)
            return updated()

        return wrapper

    return change_args
