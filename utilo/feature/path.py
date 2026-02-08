# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utilo


def connector(
    path: str,
    runner: str,
    filename: str,
    prefix: str = '',
    *,
    ftype: str = 'yaml',
) -> str:
    """Create path to resource. Replace backslash due forward slash.

    Hint: We do not check the existence of path before connecting them,
    because path can not exists.

    >>> connector('/c/gummi/', 'processor', 'info')
    '/c/gummi/processor__info.yaml'
    >>> connector('C:/', 'processor', 'info', ftype='doc')
    'C:/processor__info.doc'
    >>> connector('C:/', 'processor', 'info', ftype='')
    'C:/processor__info'
    """
    prefix = f'{prefix}_' if prefix else ''
    filename = f'{runner}__{prefix}{filename}'
    if ftype:
        filename = f'{filename}.{ftype}'
    result = os.path.join(path, filename)
    result = utilo.forward_slash(result)
    return result
