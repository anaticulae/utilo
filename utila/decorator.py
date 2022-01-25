# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
>>> import utila
>>> maximize = lambda x: utila.decorateme(x, 'maximize')

>>> @maximize
... def runtime():
...     pass

>>> assert utila.isdecorated(runtime, 'maximize')

>>> utila.decorators(runtime)
{'maximize'}
"""

import contextlib

import utila


def decorateme(method, value):
    try:
        method.__control__.add(value)
    except AttributeError:
        setattr(method, '__control__', {value})
    return method


def decorators(method) -> set:
    """\
    >>> decorators(decorators)
    {}
    """
    assert method, str(method)
    with contextlib.suppress(AttributeError):
        return method.__control__
    return {}


def isdecorated(method, name):
    return name in decorators(method)


EMPTY = object()


def empty_replace(_=None, *args, **defaultargs):  # pylint:disable=W0613,W1113
    """\
    >>> @empty_replace(member=10, glember='hello')
    ... def replace_default(first=None, member=EMPTY, glember=EMPTY):
    ...     print(first, member, glember)
    >>> replace_default('?', None)
    ? None hello
    >>> replace_default()
    None 10 hello
    >>> replace_default(1, 2, 3)
    1 2 3
    """

    def decorating_function(user_function):
        defined = set(defaultargs.keys())
        possible = set(name for (name, default) in zip(
            utila.attributes(user_function),
            utila.defaults(user_function),
        ) if default == EMPTY)
        if defined != possible:
            msg = ('Interface does not match\n'
                   f'defined: {defined}\npossible: {possible}')
            raise ValueError(msg)

        def wrapper(*args, **kwargs):
            replace_default = utila.attributes(user_function)[len(args):]
            for key in replace_default:
                if not kwargs.get(key, EMPTY) == EMPTY:
                    # TODO: MAY NOT REQUIRED
                    continue
                with contextlib.suppress(KeyError):
                    kwargs[key] = defaultargs[key]
            return user_function(*args, **kwargs)

        return wrapper

    return decorating_function
