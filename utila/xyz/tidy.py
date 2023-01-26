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

import os
import shutil
from contextlib import suppress
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from shutil import Error

import utila


def forward_slash(path: str):
    """Covert to forward slash to ease working on windows

    Replace single and multiple \\
    """
    return path.replace(r'\\', '/').replace('\\', '/')


def archive(archive_path):
    if not exists(archive_path):
        msg = '[ERROR] Path %s does not exists' % forward_slash(archive_path)
        print(msg, flush=True)
        exit(1)

    print('Tidy: %s' % forward_slash(archive_path))
    for item in os.scandir(archive_path):
        if not item.is_file() and item.name.endswith('.py'):
            continue
        try:
            project, version = item.name.split('-', maxsplit=1)
        except ValueError:
            continue

        new_path = os.path.join(archive_path, project)
        new_item_path = join(new_path, item.name)
        os.makedirs(new_path, exist_ok=True)

        if exists(new_item_path):
            print('Skip package. It already exists: %s' % new_item_path)
            continue

        with suppress(Error):
            shutil.move(item.path, new_path)


def main(cwd=None):
    if not cwd:
        cwd = utila.cwdget()
    archive(cwd)
