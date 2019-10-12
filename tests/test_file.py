#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import shutil
from os import listdir
from os import makedirs
from os.path import exists
from os.path import join

import pytest
from pytest import fixture
from pytest import raises

import utila
from utila import ROOT
from utila import assert_file
from utila import assert_html
from utila import copy_content
from utila import file_append
from utila import file_create
from utila import file_read
from utila import file_replace
from utila import from_raw_or_path
from utila import tmp
from utila import tmpfile
from utila import tmpname
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


def test_file_tmpname():
    name = tmpname(width=15)
    assert len(name) == 15, name

    name = tmpname(width=20)
    assert len(name) == 20, name


def test_file_tmpfile(tmpdir):
    random_path = tmpfile(tmpdir)
    assert not exists(random_path), random_path


def test_file_tmp_redirect(testdir, monkeypatch):
    """Redirect tmp-path with KIWI_TEMPBASE environ variable"""
    with monkeypatch.context() as context:
        context.setattr(os, 'environ', {SHARED_TEMP: str(testdir)})
        temp = tmp(ROOT)
        assert exists(temp), temp


def test_file_tmp_without_shared_temp(testdir, monkeypatch):
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


def test_file_replace_file(testdir):
    path = join(str(testdir), 'file.txt')
    assert not exists(path)

    file_replace(path, 'Content')
    assert exists(path)
    file_replace(path, 'NewContent')

    content = file_read(path)
    assert content == 'NewContent'

    # no changes in file
    file_replace(path, 'NewContent')
    content = file_read(path)
    assert content == 'NewContent'


def test_file_copy_content_file_to_directory(testdir):
    testdir = str(testdir)
    filename = 'abc.txt'
    file_create(filename)
    destination = join(testdir, 'destination')
    copy_content(filename, destination)

    assert exists(join(destination, filename))


def test_file_copy_content_file_to_file(testdir):
    testdir = str(testdir)
    filename = 'abc.txt'
    file_create(filename)
    destination = join(testdir, 'cba.txt')
    copy_content(filename, destination)

    assert exists(destination)


def test_file_copy_content_directory_to_directory(testdir):
    testdir = str(testdir)
    folder = prepare_example(testdir)

    goal = join(testdir, 'goal')
    copy_content(folder, goal)

    assert len(listdir(goal)) == 3, listdir(goal)


@pytest.mark.parametrize('skip_overwrite', [
    True,
    False,
])
def test_file_copy_content_access_error(
        skip_overwrite,
        testdir,
        monkeypatch,
        capsys,
):
    """Copy file to path which exists and is not overwriteable like an open
    pdf file.

    Create example with 2 directories called source and sink. Both
    directories contains a file named `single.pdf`. Using
    copy_content(source, sink) should raises an error, cause the sink pdf is
    locked by an pdf reader for example.

    Args:
        skip_overwrite: if True, the copy process which raises OSError is not
                        reached and therefore no SystemExit is raised.

    TODO: refactor/simplify with: file_lock/file_unlock
    """
    root = str(testdir)
    source = os.path.join(root, 'source')
    sink = os.path.join(root, 'sink')

    for item in [source, sink]:
        makedirs(item)
        pdf = os.path.join(item, 'single.pdf')
        utila.file_create(pdf)
    notdouble = os.path.join(source, 'not_double.pdf')
    utila.file_create(notdouble)

    def copy(source, dest):
        if source == notdouble:
            # notdouble is not locked, therefore no error is raised
            return
        raise OSError()

    with monkeypatch.context() as context:
        context.setattr(shutil, 'copy', copy)

        if skip_overwrite:
            utila.copy_content(source, sink, skip_overwrite=True)
            return

        with raises(SystemExit):
            utila.copy_content(
                source,
                sink,
            )
        out, err = capsys.readouterr()
        assert 'single.pdf' in err, (out + err)


def prepare_example(directory):
    folder = join(directory, 'first')

    folder_abc = join(folder, 'abc.txt')
    folder_def = join(folder, 'def.txt')
    folder_ghi = join(folder, 'ghi.txt')

    makedirs(folder)
    for item in [
            folder_abc,
            folder_def,
            folder_ghi,
    ]:
        file_create(item, item)

    return folder


@pytest.mark.parametrize('path, expected', [
    (
        'C:/folder/names/test.pdf',
        'C_folder_names_test_pdf',
    ),
    (
        'resources\\main\\examples',
        'resources_main_examples',
    ),
])
def test_file_make_single(path, expected):
    converted = utila.make_single(path)
    assert converted == expected


def test_file_make_single_shorten():
    path = 'C:/helmut/this/is/a/very/long/folder/ending.txt'
    expected_length = 20
    shorten = utila.make_single(path, length=expected_length)

    assert len(shorten) == expected_length, str(shorten)
    assert shorten.endswith('folder_ending_txt'), str(shorten)


@pytest.mark.parametrize('path, root, expected', [
    (
        'C:/folder/names/test.pdf',
        'C:/folder/',
        'names/test.pdf',
    ),
    (
        'resources\\main\\examples',
        'resources',
        'main/examples',
    ),
])
def test_file_make_relative(path, root, expected):
    converted = utila.make_relative(path, root=root)
    assert converted == expected


@pytest.mark.parametrize('filename', [
    'example.yaml',
    'example',
])
def test_file_yaml(filename):
    yaml_file = utila.yaml(filename)
    assert yaml_file == 'example.yaml'


def test_file_yaml_path_given():
    path = 'C:\\usr\\dev\\example.yaml'
    with pytest.raises(AssertionError):
        utila.yaml(path)


@pytest.mark.parametrize('first_content, second_content, expected_result', [
    ('', '', True),
    ('A', '', False),
    ('', 'This is content', False),
    ('We are equal!\nRealy!', 'We are equal!\nRealy!', True),
])
def test_file_compare(first_content, second_content, expected_result, testdir):
    root = str(testdir)

    first = os.path.join(root, 'first')
    second = os.path.join(root, 'second')

    utila.file_create(first, first_content)
    utila.file_create(second, second_content)

    equals = utila.file_compare(first, second)

    assert equals == expected_result


def test_file_compare_binary_file(testdir):
    root = str(testdir)
    utf32 = os.path.join(root, 'example.utf32')

    with open(utf32, mode='w', encoding='utf32') as fp:
        fp.write('\u1234')

    equal = utila.file_compare(utf32, __file__)
    assert not equal


def test_file_compare_not_exists():
    first = '/c/data/abc.text'
    second = __file__
    equals = utila.file_compare(first, second)
    assert equals is False

    equals = utila.file_compare(second, first)
    assert equals is False


def test_file_lock(testdir):
    root = str(testdir)
    first = os.path.join(root, 'locked.abc')

    utila.file_create(first, 'file to lock')

    assert utila.file_islocked(first) is False

    utila.file_lock(first)
    assert utila.file_islocked(first) is True

    # test write protection
    with pytest.raises(OSError):
        utila.file_remove(first)
    assert os.path.exists(first)

    utila.file_unlock(first)
    assert utila.file_islocked(first) is False

    utila.file_remove(first)
    assert not os.path.exists(first), 'write protection is already there'


@pytest.mark.parametrize('path, expected', [
    ('www/helmut/test.py', 'www.helmut.test'),
    ('www\\helmut\\test.py', 'www.helmut.test'),
    ('abc\\www\\nbc', 'abc.www.nbc'),
])
def test_file_make_package(path, expected):
    result = utila.make_package(path)

    assert result == expected, str(result)


def test_file_make_package_root():
    path = 'www/helmut/test.py'
    expected = 'helmut.test'

    result = utila.make_package(path, root='www')

    assert result == expected, str(result)
