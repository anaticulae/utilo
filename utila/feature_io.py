# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os


def pathconnector(
        path: str,
        runner: str,
        filename: str,
        prefix: str = '',
) -> str:
    assert os.path.isdir(path), str(path)
    prefix = f'{prefix}_' if prefix else ''
    filename = f'{runner}__{prefix}{filename}.yaml'
    result = os.path.join(path, filename)
    return result
