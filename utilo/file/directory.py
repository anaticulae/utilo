# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import shutil
import stat

import utilo


def directory_list(
    path: str,
    absolute: bool = False,
    recursive: bool = False,
) -> list:
    if recursive:
        absolute = True
    utilo.exists_assert(path)
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
    utilo.exists_assert(path)
    assert not utilo.isfilepath(path), path
    for item in utilo.file_list(
            path,
            absolute=True,
            recursive=recursive,
    ):
        utilo.file_lock(
            item,
            noerror=noerror,
        )


def directory_unlock(path: str, recursive: bool = True, noerror: bool = True):
    utilo.exists_assert(path)
    assert not utilo.isfilepath(path), path
    for item in utilo.file_list(
            path,
            recursive=recursive,
            absolute=True,
    ):
        utilo.file_unlock(
            item,
            noerror=noerror,
        )


def tree_remove(path: str):
    path = str(path)
    assert os.path.exists(path), path

    def remove_readonly(func, path, _):  # pylint:disable=W0613
        """Clear the readonly bit and reattempt the removal."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        shutil.rmtree(path, onerror=remove_readonly)
    except PermissionError:
        utilo.exitx(f'Could not remove {path}')
