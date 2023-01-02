# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def directory_list(
    path: str,
    absolute: bool = False,
    recursive: bool = False,
) -> list:
    if recursive:
        absolute = True
    utila.exists_assert(path)
    result = []
    for item in os.scandir(path):
        if not item.is_dir():
            continue
        if absolute:
            result.append(os.path.join(path, item.name))
        else:
            result.append(item.name)
        if recursive:
            result.extend(
                directory_list(
                    os.path.join(path, item.name),
                    absolute=absolute,
                    recursive=recursive,
                ))
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
