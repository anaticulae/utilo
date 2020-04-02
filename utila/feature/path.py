# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os


def connector(
        path: str,
        runner: str,
        filename: str,
        prefix: str = '',
        *,
        ftype: str = 'yaml',
) -> str:
    """Create path to resource.

    Hint: We do not check the existence of path before connecting them,
    because path can not exists.

    >>> connector('/c/gummi/', 'processor', 'info')
    '/c/gummi/processor__info.yaml'
    >>> connector('C:/', 'processor', 'info', ftype='doc')
    'C:/processor__info.doc'
    """
    prefix = f'{prefix}_' if prefix else ''
    filename = f'{runner}__{prefix}{filename}.{ftype}'
    result = os.path.join(path, filename)
    return result
