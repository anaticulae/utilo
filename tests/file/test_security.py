# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def test_file_create_private_str(testdir):
    content = 'This is Helmut.'
    path = os.path.join(testdir.tmpdir, 'helm.txt')
    utila.file_create(path, content, private=True)
    assert utila.file_read(path) == content


def test_file_append_private_str(testdir):
    content = 'This is Helmut.'
    path = os.path.join(testdir.tmpdir, 'helm.txt')
    utila.file_append(path, content, create=True, private=True)
    utila.file_append(path, content, private=True)
    utila.file_append(path, content, private=True)
    assert utila.file_read(path) == content + content + content


def test_file_create_private_binary(testdir):
    content = b'This is Helmut.'
    path = os.path.join(testdir.tmpdir, 'helm.txt')
    utila.file_create_binary(path, content, private=True)
    assert utila.file_read_binary(path) == content
