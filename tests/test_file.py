#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
from os import makedirs
from os.path import exists
from os.path import join

from pytest import fixture
from pytest import raises

from utila import ROOT
from utila import assert_file
from utila import assert_html
from utila import copy_content
from utila import file_append
from utila import file_create
from utila import file_read
from utila import from_raw_or_path
from utila import tempfile
from utila import tempname
from utila import tmp
from utila.file import SHARED_TEMP


def test_file_append_assert(tmpdir):
    first = join(tmpdir, 'abc.txt')
    with raises(AssertionError):
        file_append(first, '')


def test_file_append_create(tmpdir):
    first = join(tmpdir, 'abc.txt')
    file_append(first, 'BBB', create=True)
    assert exists(first)

    file_append(first, 'AAA', create=True)
    content = file_read(first)
    assert 'AAA' in content


def test_file_from_path_or_raw(tmpdir):
    content = """\
        I am The content
        to
        load and write
    """

    path = join(tmpdir, 'example.yaml')

    file_create(path, content)

    from_path = from_raw_or_path(path)
    from_raw = from_raw_or_path(content)

    assert from_raw == content
    assert from_path == from_raw

    with raises(ValueError):
        from_raw_or_path('/c/test.yaml')


def test_file_tempname():
    name = tempname(width=15)
    assert len(name) == 15, name

    name = tempname(width=20)
    assert len(name) == 20, name


def test_file_tempfile(tmpdir):
    random_path = tempfile(tmpdir)
    assert not exists(random_path), random_path


def test_file_temp_redirect(testdir, monkeypatch):
    """Redirect tmp-path with KIWI_TEMPBASE environ variable"""
    with monkeypatch.context() as context:
        context.setattr(os, 'environ', {SHARED_TEMP: str(testdir)})
        temp = tmp(ROOT)
        assert exists(temp), temp


def test_file_temp_without_shared_temp(testdir, monkeypatch):
    """Do not redirect SHARED_TEMP"""
    with monkeypatch.context() as context:
        # unset SHARED_TEMP
        context.setattr(os, 'environ', {})
        without_redirect = tmp(ROOT)
        assert without_redirect.endswith('.tmp'), without_redirect


def test_file_assert_html_files():
    files = [
        'test/abc.html',
        'test/www.html',
        'test/elfe.html',
    ]
    assert_html(files)

    with raises(AssertionError):
        assert_file(files, '.txt')


@fixture
def content_folder(tmpdir):
    root = str(tmpdir)
    file_create(join(root, 'test.txt'))
    file_create(join(root, 'abc.txt'))
    file_create(join(root, 'www.txt'))

    makedirs(join(root, 'abc', 'def', 'ghi', 'jklm'))
    file_create(join(root, 'abc/def/ghi/www.txt'))
    file_create(join(root, 'abc/def/ghi/jklm/ggg.txt'))
    return root


def test_file_copy_content_recursive(testdir, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` recursive"""
    goal = str(testdir)
    copy_content(content_folder, goal, recursive=True)

    assert exists(join(goal, 'test.txt'))
    assert exists(join(goal, 'abc.txt'))
    assert exists(join(goal, 'www.txt'))

    assert exists(join(goal, 'abc/def/ghi/jklm'))
    assert exists(join(goal, 'abc/def/ghi/www.txt'))
    assert exists(join(goal, 'abc/def/ghi/jklm/ggg.txt'))


def test_file_copy_content_recursive_false(testdir, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` non recursive"""
    goal = str(testdir)
    copy_content(content_folder, goal, recursive=False)

    assert exists(join(goal, 'test.txt'))
    assert exists(join(goal, 'abc.txt'))
    assert exists(join(goal, 'www.txt'))

    assert exists(join(goal, 'abc'))
