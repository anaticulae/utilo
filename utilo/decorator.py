# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
>>> import utilo
>>> maximize = lambda x: utilo.decorateme(x, 'maximize')

>>> @maximize
... def runtime():
...     pass

>>> assert utilo.isdecorated(runtime, 'maximize')

>>> utilo.decorators(runtime)
{'maximize'}
"""

import contextlib

import utilo


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
            utilo.attributes(user_function),
            utilo.defaults(user_function),
        ) if default == EMPTY)
        if defined != possible:
            msg = ('Interface does not match\n'
                   f'defined: {defined}\npossible: {possible}')
            raise ValueError(msg)

        def wrapper(*args, **kwargs):
            replace_default = utilo.attributes(user_function)[len(args):]
            for key in replace_default:
                if not kwargs.get(key, EMPTY) == EMPTY:
                    # TODO: MAY NOT REQUIRED
                    continue
                with contextlib.suppress(KeyError):
                    kwargs[key] = defaultargs[key]
            return user_function(*args, **kwargs)

        return wrapper

    return decorating_function
