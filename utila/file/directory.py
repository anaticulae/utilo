# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def directory_list(path: str) -> list:
    utila.exists_assert(path)
    result = []
    for item in os.scandir(path):
        if not item.is_dir():
            continue
        result.append(item.name)
    return result


def directory_lock(path: str, recursive: bool = True, noerror: bool = True):
    utila.exists_assert(path)
    assert not utila.isfilepath(path), path
    for item in utila.file_list(
            path,
            absolute=True,
            recursive=recursive,
    ):
        utila.file_lock(
            item,
            noerror=noerror,
        )


def directory_unlock(path: str, recursive: bool = True, noerror: bool = True):
    utila.exists_assert(path)
    assert not utila.isfilepath(path), path
    for item in utila.file_list(
            path,
            recursive=recursive,
            absolute=True,
    ):
        utila.file_unlock(
            item,
            noerror=noerror,
        )
