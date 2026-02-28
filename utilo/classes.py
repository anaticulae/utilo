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
>>> collected = collect_classes(utilo)
>>> name_classes(collected)
{...>, 'TablePrinter': <class 'utilo.string.table.TablePrinter'>...}
"""

import inspect

import utilo


def collect_classes(classes, valid=None):
    """Collect classes from given list of modules. Use `valid` to
    precise selection.

    >>> import utilo.collection
    >>> collect_classes(utilo.collection, valid=lambda x: 'Buckets' in x.__name__)
    (<class 'utilo.collection.Buckets'>,)
    >>> collect_classes((utilo.collection,), valid=lambda x: 'Buckets' in x.__name__)
    (<class 'utilo.collection.Buckets'>,)
    """
    if not utilo.iterable(classes):
        classes = (classes,)
    if not valid:
        valid = utilo.sall_true
    result = []
    for item in classes:
        for value in vars(item).values():
            if not inspect.isclass(value):
                continue
            if not valid(value):
                continue
            result.append(value)
    result: tuple = tuple(result)
    return result


def name_classes(classes) -> dict:
    result = {item.__name__: item for item in classes}
    return result
