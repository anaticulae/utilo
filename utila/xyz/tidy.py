# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
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

import utila


def archive(archive_path):
    if not utila.exists(archive_path):
        msg = f'[ERROR] Path {utila.forward_slash(archive_path)} does not exists'
        utila.exitx(msg)
    utila.log(f'Tidy: {utila.forward_slash(archive_path)}')
    for item in os.scandir(archive_path):
        if not item.is_file() and item.name.endswith('.py'):
            continue
        try:
            project, version = item.name.split('-', maxsplit=1)
        except ValueError:
            continue

        new_path = utila.join(archive_path, project)
        new_item_path = utila.join(new_path, item.name)
        os.makedirs(new_path, exist_ok=True)

        if utila.exists(new_item_path):
            utila.log('Skip package. It already exists: {new_item_path}')
            continue
        with contextlib.suppress(shutil.Error):
            shutil.move(item.path, new_path)
    utila.exitx('done', returncode=utila.SUCCESS)


def main(cwd=None):
    if not cwd:
        cwd = utila.cwdget()
    archive(cwd)
