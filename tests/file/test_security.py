# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utilo


def test_file_create_private_str(td):
    content = 'This is Helmut.'
    path = os.path.join(td.tmpdir, 'helm.txt')
    utilo.file_create(path, content, private=True)
    assert utilo.file_read(path) == content


def test_file_append_private_str(td):
    content = 'This is Helmut.'
    path = os.path.join(td.tmpdir, 'helm.txt')
    utilo.file_append(path, content, create=True, private=True)
    utilo.file_append(path, content, private=True)
    utilo.file_append(path, content, private=True)
    assert utilo.file_read(path) == content + content + content


def test_file_create_private_binary(td):
    content = b'This is Helmut.'
    path = os.path.join(td.tmpdir, 'helm.txt')
    utilo.file_create_binary(path, content, private=True)
    assert utilo.file_read_binary(path) == content


def test_copy_content_private(td):
    td.mkdir('open')
    td.mkdir('second')

    utilo.file_create('open/public.txt', utilo.file_read(__file__))
    binary_content = b'\xAA& Binary Content &\n'
    utilo.file_create_binary('second/binary.txt', binary_content)

    utilo.copy_content('.', 'private', recursive=True, private=True)

    public = utilo.file_read('private/open/public.txt')
    assert public == utilo.file_read(__file__)
    binary = utilo.file_read_binary('private/second/binary.txt')
    assert binary == binary_content
