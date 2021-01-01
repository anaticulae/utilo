# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os


def directory_list(path: str) -> list:
    assert os.path.exists(path), path
    result = []
    for item in os.scandir(path):
        if not item.is_dir():
            continue
        result.append(item.name)
    return result
