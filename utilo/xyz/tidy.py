# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""This script converts a list of package into the pypi-compatible structure

The filename is splitted by version token `-` and saved under
projectname/projectname-version. This operation is executed in place for
**internal** and **external** package-repository.
"""

import contextlib
import os
import shutil

import utilo


def archive(archive_path):
    if not utilo.exists(archive_path):
        msg = f'[ERROR] Path {utilo.forward_slash(archive_path)} does not exists'
        utilo.exitx(msg)
    utilo.log(f'Tidy: {utilo.forward_slash(archive_path)}')
    for item in os.scandir(archive_path):
        if not item.is_file() and item.name.endswith('.py'):
            continue
        project = package_name(item.name)
        new_path = utilo.join(archive_path, project)
        new_item_path = utilo.join(new_path, item.name)
        os.makedirs(new_path, exist_ok=True)
        if utilo.exists(new_item_path):
            utilo.log(f'Skip package. It already exists: {new_item_path}')
            continue
        with contextlib.suppress(shutil.Error):
            shutil.move(item.path, new_path)
    utilo.exitx('done', returncode=utilo.SUCCESS)


SPLIT = utilo.compiles(r'-\d{1,3}\.?')


def package_name(name: str) -> str:
    """\
    >>> package_name('argon2_cffi-20.1.0-cp37-cp37m-win32.whl')
    'argon2_cffi'
    >>> package_name('pytest-konira-0.2.tar.gz')
    'pytest-konira'
    >>> package_name('astor')
    'astor'
    """
    name = SPLIT.split(name, maxsplit=1)[0]
    return name


def main(cwd=None):
    if not cwd:
        cwd = utilo.cwdget()
    archive(cwd)
