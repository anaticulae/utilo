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
from utila import file_read


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
