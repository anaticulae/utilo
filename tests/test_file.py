#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import shutil

import pytest
import yaml

import utila
import utila.file


def test_file_append_assert(tmpdir):
    first = os.path.join(tmpdir, 'abc.txt')
    with pytest.raises(AssertionError):
        utila.file_append(first, '')


def test_file_append_create(tmpdir):
    first = os.path.join(tmpdir, 'abc.txt')
    utila.file_append(first, 'BBB', create=True)
    assert os.path.exists(first)

    utila.file_append(first, 'AAA', create=True)
    content = utila.file_read(first)
    assert 'AAA' in content


def test_file_from_path_or_raw(tmpdir):
    content = """\
        I am The content
        to
        load and write
    """

    path = os.path.join(tmpdir, 'example.yaml')
    utila.file_create(path, content)

    from_path = utila.from_raw_or_path(path)
    from_raw = utila.from_raw_or_path(content)

    assert from_raw == content
    assert from_path == from_raw


def test_file_from_path_or_raw_default(testdir):
    root = str(testdir.tmpdir)
    utila.file_create(os.path.join(root, 'example.yaml'), 'defaultcontent')
    default = utila.from_raw_or_path(root, ftype='yaml', fname='example')
    assert default == 'defaultcontent'


def test_file_from_path_or_raw_default_not_exists(testdir):
    root = str(testdir.tmpdir)
    with pytest.raises(FileNotFoundError):
        utila.from_raw_or_path(root, ftype='yaml', fname='abc')


def test_file_from_path_or_raw_not_exists():
    with pytest.raises(FileNotFoundError):
        utila.from_raw_or_path('/c/test.yaml')


def test_yaml_from_path(testdir):
    dumped = yaml.dump(['test', 'data'])
    utila.file_create('test.yaml', dumped)

    def verify(item):
        assert len(item) == 2

    loaded = utila.yaml_from_raw_or_path('test.yaml', verify=verify)
    assert len(loaded) == 2
    loaded = utila.yaml_from_raw_or_path('test.yaml', safe=False)
    assert len(loaded) == 2


def test_file_tmpname():
    name = utila.tmpname(width=15)
    assert len(name) == 15, name

    name = utila.tmpname(width=20)
    assert len(name) == 20, name


def test_file_tmpfile(tmpdir):
    random_path = utila.tmpfile(tmpdir)
    assert not os.path.exists(random_path), random_path


def test_file_tmp_redirect(testdir, monkeypatch):
    """Redirect tmp-path with KIWI_TEMPBASE environ variable"""
    with monkeypatch.context() as context:
        context.setattr(os, 'environ', {utila.file.SHARED_TEMP: str(testdir)})
        temp = utila.tmp(utila.ROOT)
        assert os.path.exists(temp), temp


def test_file_tmp_without_shared_temp(testdir, monkeypatch):
    """Do not redirect SHARED_TEMP"""
    with monkeypatch.context() as context:
        # unset SHARED_TEMP
        context.setattr(os, 'environ', {})
        without_redirect = utila.tmp(utila.ROOT)
        assert without_redirect.endswith('.tmp'), without_redirect


def test_file_assert_html_files():
    files = [
        'test/abc.html',
        'test/www.html',
        'test/elfe.html',
    ]
    utila.assert_html(files)

    with pytest.raises(AssertionError):
        utila.assert_file(files, '.txt')


@pytest.fixture
def content_folder(tmpdir):
    root = str(tmpdir)
    utila.file_create(os.path.join(root, 'test.txt'))
    utila.file_create(os.path.join(root, 'abc.txt'))
    utila.file_create(os.path.join(root, 'www.txt'))

    os.makedirs(os.path.join(root, 'abc', 'def', 'ghi', 'jklm'))
    utila.file_create(os.path.join(root, 'abc/def/ghi/www.txt'))
    utila.file_create(os.path.join(root, 'abc/def/ghi/jklm/ggg.txt'))
    return root


def test_file_copy_content_recursive(testdir, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` recursive"""
    goal = str(testdir)
    utila.copy_content(content_folder, goal, recursive=True)

    assert os.path.exists(os.path.join(goal, 'test.txt'))
    assert os.path.exists(os.path.join(goal, 'abc.txt'))
    assert os.path.exists(os.path.join(goal, 'www.txt'))

    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/jklm'))
    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/www.txt'))
    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/jklm/ggg.txt'))


def test_file_copy_content_verbose(testdir, content_folder, capsys):  #pylint:disable=W0621
    """Test that operation are logged to console"""
    goal = str(testdir)
    utila.copy_content(content_folder, goal, recursive=True, verbose=True)

    stdout = capsys.readouterr().out

    assert stdout.count('mkdir:') == 4, stdout
    assert stdout.count('cp:') == 5, stdout


def test_file_copy_content_recursive_false(testdir, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` non recursive"""
    goal = str(testdir)
    utila.copy_content(content_folder, goal, recursive=False)

    assert os.path.exists(os.path.join(goal, 'test.txt'))
    assert os.path.exists(os.path.join(goal, 'abc.txt'))
    assert os.path.exists(os.path.join(goal, 'www.txt'))

    assert os.path.exists(os.path.join(goal, 'abc'))


@pytest.mark.parametrize(
    'pattern, recursive, expected',
    [
        ('*.txt', True, 3),
        ('*.txt', False, 3),
        (r'*.pdf', True, 0),
        (r'*.pdf', False, 0),
        (None, True, 4),
        (None, False, 4),
    ],
    ids=[
        'txt_recursive',
        'txt',
        'pdf',
        'pdf_recursive',
        'None',
        'None_recursive',
    ],
)
def test_file_copy_content_pattern(
        pattern,
        recursive,
        expected,
        testdir,
        content_folder,
):  # pylint:disable=W0621
    source = content_folder
    utila.file_create(os.path.join(source, 'hallotxt'))

    root = str(testdir)

    utila.copy_content(source, root, pattern=pattern, recursive=recursive)
    files = [item for item in os.listdir(root) if utila.isfilepath(item)]
    assert len(files) == expected, root


def test_file_replace_file(testdir):
    path = os.path.join(str(testdir), 'file.txt')
    assert not os.path.exists(path)

    utila.file_replace(path, 'Content')
    assert os.path.exists(path)
    utila.file_replace(path, 'NewContent')

    content = utila.file_read(path)
    assert content == 'NewContent'

    # no changes in file
    utila.file_replace(path, 'NewContent')
    content = utila.file_read(path)
    assert content == 'NewContent'


def test_file_copy_content_file_to_directory(testdir):
    testdir = str(testdir)
    filename = 'abc.txt'
    utila.file_create(filename)
    destination = os.path.join(testdir, 'destination')
    utila.copy_content(filename, destination)

    assert os.path.exists(os.path.join(destination, filename))


def test_file_copy_content_file_to_file(testdir):
    testdir = str(testdir)
    filename = 'abc.txt'
    utila.file_create(filename)
    destination = os.path.join(testdir, 'cba.txt')
    utila.copy_content(filename, destination)

    assert os.path.exists(destination)


def test_file_copy_content_directory_to_directory(testdir):
    testdir = str(testdir)
    folder = prepare_example(testdir)

    goal = os.path.join(testdir, 'goal')
    utila.copy_content(folder, goal)

    assert len(os.listdir(goal)) == 3, os.listdir(goal)


@pytest.mark.parametrize('update', [
    True,
    False,
])
def test_file_copy_content_access_error(
        update,
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

    update: if True, the copy process which raises OSError is
            not reached and therefore no SystemExit is raised.
    monkeypatch: patch copy command to introduce overwrite error

    TODO: refactor/simplify with: file_lock/file_unlock
    """
    root = str(testdir)
    source = os.path.join(root, 'source')
    sink = os.path.join(root, 'sink')

    for item in [source, sink]:
        os.makedirs(item)
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

        if update:
            utila.copy_content(source, sink, update=True)
            return

        with pytest.raises(SystemExit):
            utila.copy_content(
                source,
                sink,
            )
        out, err = capsys.readouterr()
        assert 'single.pdf' in err, (out + err)


def prepare_example(directory):
    folder = os.path.join(directory, 'first')

    folder_abc = os.path.join(folder, 'abc.txt')
    folder_def = os.path.join(folder, 'def.txt')
    folder_ghi = os.path.join(folder, 'ghi.txt')

    os.makedirs(folder)
    for item in [
            folder_abc,
            folder_def,
            folder_ghi,
    ]:
        utila.file_create(item, item)

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


def test_file_copy_single_file(testdir):
    root = str(testdir)
    source = os.path.join(root, 'source')
    dest = os.path.join(root, 'destination')
    os.makedirs(source)
    os.makedirs(dest)

    sourcefile = os.path.join(source, 'hello')
    utila.file_create(sourcefile)

    utila.file_copy(sourcefile, dest)
    assert os.path.exists(os.path.join(dest, 'hello'))


def test_file_copy_content_mult(testdir):
    testdir.mkdir('source')
    utila.file_create('source/groupme__selm.yaml')
    utila.file_create('source/rawmaker__helm.yaml')
    testdir.mkdir('dest')

    utila.copy_content(
        'source',
        'dest',
        pattern='(rawmaker|groupme)__*.yaml',
        recursive=True,
        verbose=True,
    )
    assert os.path.exists('dest/groupme__selm.yaml')
    assert os.path.exists('dest/rawmaker__helm.yaml')


def test_file_count(tmpdir):
    assert utila.file_count(tmpdir) == 0

    with utila.chdir(tmpdir):
        utila.file_create('hi.yaml')
        utila.file_create('hi.txt')

    assert utila.file_count(tmpdir, ext='yaml') == 1
    assert utila.file_count(tmpdir) == 2


def test_file_tmpdir(testdir):
    create = utila.tmpdir(testdir.tmpdir)
    assert os.path.exists(create), create


def test_file_replace_binary(tmpdir):
    path = os.path.join(tmpdir, 'file.hex')
    utila.file_replace_binary(path, b'Helm')
    # replace content
    utila.file_replace_binary(path, b'Helm2')
    # do nothing
    utila.file_replace_binary(path, b'Helm2')


def test_file_list():
    files = utila.file_list(utila.ROOT)
    assert files

    txt = utila.file_list(utila.ROOT, include='txt')
    assert len(txt) <= len(files)

    py = utila.file_list(utila.ROOT, include='py')  # pylint:disable=C0103
    assert len(py) > len(txt)

    py_txt = utila.file_list(utila.ROOT, include=['py', 'txt'])
    assert len(py_txt) == (len(txt) + len(py))

    exclude_txt = utila.file_list(utila.ROOT, exclude='txt')
    assert len(exclude_txt) == (len(files) - len(txt))


def test_file_list_relative(testdir):
    utila.file_create('test.txt')
    files = utila.file_list(testdir.tmpdir)
    assert files == ['test.txt']
    files = utila.file_list(testdir.tmpdir, absolute=True)
    assert files != ['test.txt']


def test_make_tmpdir(testdir):
    root = testdir.tmpdir
    with utila.make_tmpdir(root) as tmp_dir:
        assert os.path.exists(tmp_dir)
    assert os.path.exists(tmp_dir)


def test_make_tmpdir_remove(testdir):
    root = testdir.tmpdir
    with utila.make_tmpdir(root, remove=True) as tmp_dir:
        assert os.path.exists(tmp_dir)
        os.makedirs(os.path.join(tmp_dir, 'recursive_path'))
        utila.file_create(os.path.join(tmp_dir, 'helm.txt'))
    assert not os.path.exists(tmp_dir), tmp_dir


def test_directory_list(testdir):
    os.makedirs('abc')
    os.makedirs('abcd')
    utila.file_create('abc.txt')
    listed = utila.directory_list(testdir.tmpdir)
    assert len(listed) == 2
