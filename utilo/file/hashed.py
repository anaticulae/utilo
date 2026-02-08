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


def file_hash(path: str) -> str:
    utilo.exists_assert(path)
    content = utilo.file_read_binary(path)
    hashed = utilo.freehash(content)
    return hashed


def directory_hash(paths: str, *, ftype='yaml') -> str:
    paths = [paths] if isinstance(paths, str) else paths
    if not paths:
        return None
    collected = []
    for path in paths:
        if os.path.isfile(path):  # pylint:disable=W0160
            files = [path]
        else:
            files = utilo.file_list(
                path,
                include=ftype,
                recursive=True,
            )
        for filepath in files:
            hashed = file_hash(filepath)
            collected.append(hashed)
    if not files:
        return None
    merged = utilo.NEWLINE.join(collected)
    return utilo.freehash(merged)
