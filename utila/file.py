#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os import makedirs
from os import remove
from os.path import exists
from os.path import isfile
from os.path import join

from utila.utils import NEWLINE
from utila.utils import TMP
from utila.utils import UTF8


def tmp(root):
    """Return path to temporary folder. If not exists, create folder

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root
    path = join(root, TMP)
    makedirs(path, exist_ok=True)
    return path


def assert_path(path: str):
    if not exists(path):
        raise ValueError('Path does not exists: ' % path)


def file_append(path: str, content: str, create: bool = False):
    """Append `content` to file given in `path`.

    Args:
        path(str): file to write
        content(str): write content to file
        create(bool): if True, create File if not exists

    Hint:
        If file not exists and create == False,  an assertion is fired.
    """
    if not create:
        assert exists(path)
    if not exists(path):
        file_create(path, content)
    else:
        with open(path, mode='a', newline=NEWLINE, encoding=UTF8) as fp:
            fp.write(content)


def file_create(path: str, content: str = ''):
    assert not exists(path)
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
    assert isinstance(content, str)
    if content.endswith('.%s' % ftype) and not exists(content):
        raise ValueError('File does not exists: %s' % content)

    # filepath must not have any linebreaks
    if len(content.splitlines()) == 1 and isfile(content):
        content = file_read(content)
    return content
