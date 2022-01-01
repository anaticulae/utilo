# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
# Example

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


def decorateme(method, value):
    try:
        method.__control__.add(value)
    except AttributeError:
        setattr(method, '__control__', {value})
    return method


def decorators(method) -> set:
    assert method, str(method)
    with contextlib.suppress(AttributeError):
        return method.__control__
    return {}


def isdecorated(method, name):
    return name in decorators(method)
