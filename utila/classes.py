# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import inspect


def collect_classes(classes, valid=None):
    """Collect classes from given list of modules. Use `valid` to
    precise selection.

    >>> import utila.collection
    >>> collect_classes(utila.collection, valid=lambda x: 'Buckets' in x.__name__)
    (<class 'utila.collection.Buckets'>,)
    """
    if not isinstance(classes, (list, tuple)):
        classes = (classes,)
    if not valid:
        valid = lambda x: True
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
