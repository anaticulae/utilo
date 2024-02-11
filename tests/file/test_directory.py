# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def test_directory_lock(tmpdir):
    write = tmpdir.mkdir('sub').join('hello.txt')
    write.write('content')
    utila.directory_lock(tmpdir)
    assert utila.file_islocked(write)
    utila.directory_unlock(tmpdir)
    assert not utila.file_islocked(write)


def test_directory_list_noparam(td):
    td.tmpdir.mkdir('abc')
    td.tmpdir.mkdir('abcd')
    utila.file_create('abc.txt')
    listed = utila.directory_list(td.tmpdir)
    assert len(listed) == 2


def test_directory_list_recursive_absolute():
    directories = utila.directory_list(
        utila.ROOT,
        recursive=True,
        absolute=True,
    )
    assert len(directories) > 40


def test_tree_remove(testdir):
    testdir.tmpdir.mkdir('test')
    testdir.tmpdir.mkdir('test/abc')
    assert len(utila.directory_list(testdir.tmpdir)) == 1
    utila.tree_remove(testdir.tmpdir.join('test'))
    assert not utila.directory_list(testdir.tmpdir)
