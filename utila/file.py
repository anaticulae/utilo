#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
from os import listdir
from os import makedirs
from os import remove
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from random import randrange
from shutil import copy

from utila.logging import logging_error
from utila.utils import NEWLINE
from utila.utils import TMP
from utila.utils import UTF8

# width of tempfile name
MAX_NUMBER = 20
SHARED_TEMP = 'SHARED_TMP'


def tmp(root) -> str:
    """Return path to temporary folder. If not exists, create folder

    To redirect the tempbase, define `KIWI_TEMPBASE` as a global envionment
    variable. The temp folder is created in this folder under the name of the
    given project, defined in `root` variable.

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root

    try:
        # redirect temp folder to central folder, defined in `SHARED_TEMP`.
        # we need control about temp folder. Temp folder must not exist in
        # site-packages, so `SHARED_TEMP` is required.
        _, projectname = split(root)
        path = join(os.environ[SHARED_TEMP], projectname)
    except KeyError:
        path = join(root, TMP)
    makedirs(path, exist_ok=True)
    return path


def file_append(path: str, content: str, create: bool = False):
    """Append `content` to file given in `path`.

    Args:
        path(str): file to write
        content(str): write content to file
        create(bool): if True, create File if not exists

    Hint:
        If file not exists and create == False, an assertion is fired.
    """
    if not create:
        assert exists(path)
    if not exists(path):
        file_create(path, content)
    else:
        with open(path, mode='a', newline=NEWLINE, encoding=UTF8) as fp:
            fp.write(content)


def file_create(path: str, content: str = ''):
    """Create file `path` with the content `content`

    Args:
        path(str): path to write file, path must not exists
        content(str): content to write in given `path`

    Hint:
        If file exists, an assertion is raised.
    """

    assert not exists(path), 'File already exists: %s' % path
    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def file_read(path: str):
    assert exists(path), path
    with open(path, mode='r', newline=NEWLINE, encoding=UTF8) as fp:
        return fp.read()


def file_remove(path: str):
    assert exists(path), path
    assert isfile(path), path
    remove(path)


def file_replace(path: str, content: str):
    """Replace file content

    1. If not exit, create file
    2. If exists,   compare content, if changed than replace
                                     if not, do nothing
    Args:
        path(str): path to file
        content(str): content to write
    """
    if not exists(path):
        file_create(path, content)
        return
    current_content = file_read(path)
    if current_content == content:
        return

    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def copy_content(source: str, destination: str, recursive: bool = False):
    """Copy the content from `source` to `destination` folder. If `desitination`
    folder does not exists, it will be created.

    Hint:
        Why not using shutil.copytree?: Copy tree expect that destination does
        not exists, but we need this.
    """
    assert exists(source)
    makedirs(destination, exist_ok=True)
    for item in listdir(source):
        source_ = join(source, item)
        dest_ = join(destination, item)
        if isfile(source_):
            # copy files
            copy(source_, dest_)
        else:
            # 'copy' folder
            makedirs(dest_)
            if recursive:
                copy_content(source_, dest_, recursive=True)


def from_raw_or_path(content: str, ftype: str = 'yaml'):
    """Provide raw content from file or pass content

    This method enables the interface to get content from filepath or use
    direct raw content.

    Args:
        content(str): filepath or raw content
        ftype(str): file type which is checked
    Returns:
        loaded content or raw passed content
    """
    assert isinstance(content, str), 'Require `str` %s' % type(content)
    if content.endswith('.%s' % ftype) and not exists(content):
        raise ValueError('File does not exists: %s' % content)

    # filepath must not have any linebreaks
    if len(content.splitlines()) == 1 and isfile(content):
        content = file_read(content)
    return content


def tempname(width: int = MAX_NUMBER) -> str:
    """Get random file-name with 20-ziffre, random name

    Args:
        width(int): length of tempname
    Returns:
        filename(str): random file name
    """
    assert width
    max_test_number = 10**width

    return str(randrange(max_test_number)).zfill(width)


def tempfile(root):
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert exists(root)
    tmppath = tmp(root)

    name = 'temp%s' % tempname()
    path = join(tmppath, name)
    if exists(path):
        # try again to find unused temp file
        return tempfile(root)
    return path


def assert_file(files, filetype: str):
    """Ensure that the given `files` have the correct `filetype`

    Args:
        List[str]: list with files
        filetype(str): filetype without leading dot
    Returns:
        raises assertion when passing invalid files
    """
    # support passing single str
    files = [files] if isinstance(files, str) else files
    # ensure passing without dot
    filetype = filetype[1:] if filetype[0] == '.' else filetype
    raises = 0
    for item in files:
        if not item.endswith('.%s' % filetype):
            logging_error('No %s file: %s' % (filetype, item))
            raises += 1
    assert not raises, 'wrong file types'


def assert_html(files):
    """Ensure that all given `files` are `html` files"""
    assert_file(files, 'html')


def assert_yaml(files):
    """Ensure that all given `files` are `yaml` files"""
    assert_file(files, 'yaml')


def assert_json(files):
    """Ensure that all given `files` are `json` files"""
    assert_file(files, 'json')
