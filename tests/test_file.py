#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import exists
from os.path import join

from pytest import raises

from utila import assert_path
from utila import file_append
from utila import file_create
from utila import file_read
from utila import from_raw_or_path
from utila import tempfile
from utila import tempname


def test_assert_path(tmpdir):
    assert_path(tmpdir)


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


def test_from_path_or_raw(tmpdir):
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


def test_tempname():
    name = tempname(width=15)
    assert len(name) == 15, name

    name = tempname(width=20)
    assert len(name) == 20, name


def test_tempfile(tmpdir):
    random_path = tempfile(tmpdir)

    assert not exists(random_path), random_path
