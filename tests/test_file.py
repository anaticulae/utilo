#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import pytest
import utilatest

import utilo
import utilo.file
import utilo.file.securewrapper


def test_file_append_assert(tmpdir):
    first = os.path.join(tmpdir, 'abc.txt')
    with pytest.raises(AssertionError):
        utilo.file_append(first, '')


def test_file_append_create(tmpdir):
    first = os.path.join(tmpdir, 'abc.txt')
    utilo.file_append(first, 'BBB', create=True)
    assert os.path.exists(first)

    utilo.file_append(first, 'AAA', create=True)
    content = utilo.file_read(first)
    assert 'AAA' in content


def test_file_from_path_or_raw(tmpdir):
    content = """\
        I am The content
        to
        load and write
    """

    path = os.path.join(tmpdir, 'example.yaml')
    utilo.file_create(path, content)

    from_path = utilo.from_raw_or_path(path)
    from_raw = utilo.from_raw_or_path(content)

    assert from_raw == content
    assert from_path == from_raw


def test_file_from_path_or_raw_default(tmpdir):
    path = tmpdir.join('example.yaml')
    utilo.file_create(path, 'defaultcontent')
    default = utilo.from_raw_or_path(
        path,
        ftype='yaml',
        fname='example',
    )
    assert default == 'defaultcontent'


def test_file_from_path_or_raw_default_not_exists(td):
    root = str(td.tmpdir)
    with pytest.raises(FileNotFoundError):
        utilo.from_raw_or_path(root, ftype='yaml', fname='abc')


def test_file_from_path_or_raw_not_exists():
    with pytest.raises(FileNotFoundError):
        utilo.from_raw_or_path('/c/test.yaml')


@pytest.mark.usefixtures('testdir')
def test_yaml_from_path():
    dumped = utilo.yaml_dump(['test', 'data'])
    utilo.file_create('test.yaml', dumped)

    def verify(item):
        assert len(item) == 2

    loaded = utilo.yaml_load('test.yaml', verify=verify)
    assert len(loaded) == 2
    loaded = utilo.yaml_load('test.yaml', safe=False)
    assert len(loaded) == 2


def test_file_tmpname():
    name = utilo.tmpname(width=15)
    assert len(name) == 15, name

    name = utilo.tmpname(width=20)
    assert len(name) == 20, name


def test_file_tmpfile():
    random_path = utilo.tmpfile(utilo.ROOT)
    assert not os.path.exists(random_path), random_path


def test_file_tmp_redirect(td, mp):
    """Redirect tmp-path with KIWI_TEMPBASE environ variable"""
    with mp.context() as context:
        context.setattr(os, 'environ', {utilo.file.SHARED_TMP: str(td)})
        temp = utilo.tmp(utilo.ROOT)
        assert os.path.exists(temp), temp


def test_file_assert_html_files():
    files = [
        'test/abc.html',
        'test/www.html',
        'test/elfe.html',
    ]
    utilo.assert_html(files)

    with pytest.raises(AssertionError):
        utilo.assert_file(files, '.txt')


@pytest.fixture
def content_folder(tmpdir):
    root = str(tmpdir)
    utilo.file_create(os.path.join(root, 'test.txt'))
    utilo.file_create(os.path.join(root, 'abc.txt'))
    utilo.file_create(os.path.join(root, 'www.txt'))

    os.makedirs(os.path.join(root, 'abc', 'def', 'ghi', 'jklm'))
    utilo.file_create(os.path.join(root, 'abc/def/ghi/www.txt'))
    utilo.file_create(os.path.join(root, 'abc/def/ghi/jklm/ggg.txt'))
    return root


def test_file_copy_content_recursive(td, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` recursive"""
    goal = str(td)
    utilo.copy_content(content_folder, goal, recursive=True)

    assert os.path.exists(os.path.join(goal, 'test.txt'))
    assert os.path.exists(os.path.join(goal, 'abc.txt'))
    assert os.path.exists(os.path.join(goal, 'www.txt'))

    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/jklm'))
    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/www.txt'))
    assert os.path.exists(os.path.join(goal, 'abc/def/ghi/jklm/ggg.txt'))


def test_file_copy_content_verbose(td, content_folder, capsys):  #pylint:disable=W0621
    """Test that operation are logged to console"""
    goal = str(td)
    utilo.copy_content(content_folder, goal, recursive=True, verbose=True)

    stdout = capsys.readouterr().out

    assert stdout.count('mkdir:') == 4, stdout
    assert stdout.count('cp:') == 5, stdout


def test_file_copy_content_recursive_false(td, content_folder):  #pylint:disable=W0621
    """Test to copy `content_folder` non recursive"""
    goal = str(td)
    utilo.copy_content(content_folder, goal, recursive=False)

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
    td,
    content_folder,
):  # pylint:disable=W0621
    source = content_folder
    utilo.file_create(os.path.join(source, 'hallotxt'))

    root = str(td)

    utilo.copy_content(source, root, pattern=pattern, recursive=recursive)
    files = [item for item in os.listdir(root) if utilo.isfilepath(item)]
    assert len(files) == expected, root


def test_file_replace_file(td):
    path = os.path.join(str(td), 'file.txt')
    assert not os.path.exists(path)

    utilo.file_replace(path, 'Content')
    assert os.path.exists(path)
    utilo.file_replace(path, 'NewContent')

    content = utilo.file_read(path)
    assert content == 'NewContent'

    # no changes in file
    utilo.file_replace(path, 'NewContent')
    content = utilo.file_read(path)
    assert content == 'NewContent'


def test_file_copy_content_file_to_directory(td):
    td = str(td)
    filename = 'abc.txt'
    utilo.file_create(filename)
    destination = os.path.join(td, 'destination')
    utilo.copy_content(filename, destination)

    assert os.path.exists(os.path.join(destination, filename))


def test_file_copy_content_file_to_file(td):
    td = str(td)
    filename = 'abc.txt'
    utilo.file_create(filename)
    destination = os.path.join(td, 'cba.txt')
    utilo.copy_content(filename, destination)

    assert os.path.exists(destination)


def test_file_copy_content_directory_to_directory(td):
    td = str(td)
    folder = prepare_example(td)

    goal = os.path.join(td, 'goal')
    utilo.copy_content(folder, goal)

    assert len(os.listdir(goal)) == 3, os.listdir(goal)


@pytest.mark.parametrize('update', [
    True,
    False,
])
def test_file_copy_content_access_error(
    update,
    td,
    mp,
    capsys,
):
    """Copy file to path which exists and is not overwriteable like an
    open pdf file.

    Create example with 2 directories called source and sink. Both
    directories contains a file named `single.pdf`. Using
    copy_content(source, sink) should raises an error, cause the sink
    pdf is locked by an pdf reader for example.

    update: if True, the copy process which raises OSError is
            not reached and therefore no SystemExit is raised.
    mp: patch copy command to introduce overwrite error

    TODO: refactor/simplify with: file_lock/file_unlock
    """
    root = str(td)
    source = os.path.join(root, 'source')
    sink = os.path.join(root, 'sink')

    for item in [source, sink]:
        os.makedirs(item)
        pdf = os.path.join(item, 'single.pdf')
        utilo.file_create(pdf)
    notdouble = os.path.join(source, 'not_double.pdf')
    utilo.file_create(notdouble)

    def copy(source, _, private: bool = False):  # pylint:disable=W0613
        if source == notdouble:
            # not double is not locked, therefore no error is raised
            return
        raise OSError()

    with mp.context() as context:
        context.setattr(utilo.file.securewrapper, 'copy', copy)
        context.setattr(utilo, 'file_age_update', lambda path, seconds: True)  # pylint:disable=C3001
        if update:
            utilo.copy_content(source, sink, update=True)
            return
        with pytest.raises(SystemExit):
            utilo.copy_content(
                source,
                sink,
            )
        out, err = capsys.readouterr()
        assert 'single.pdf' in err, (out + err)


def test_file_copy_lock_nolock(testdir):
    locked = testdir.tmpdir.join('path')
    utilo.file_create(locked, content='locked')
    utilo.file_lock(locked)
    utilo.file_islocked(locked)
    # copy without lock
    unlocked = testdir.tmpdir.join('unlocked')
    utilo.copy_content(src=locked, dst=unlocked, unlock=True)
    assert not utilo.file_islocked(unlocked.join('path'))


def test_file_copy_lock_withlock(testdir):
    locked = testdir.tmpdir.join('path')
    utilo.file_create(locked, content='locked')
    utilo.file_lock(locked)
    # copy with lock
    skip_unlock = testdir.tmpdir.join('superlock')
    utilo.copy_content(src=locked, dst=skip_unlock)
    assert utilo.file_islocked(skip_unlock.join('path'))


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
        utilo.file_create(item, item)

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
    converted = utilo.make_single(path)
    assert converted == expected


def test_file_make_single_shorten():
    path = 'C:/helmut/this/is/a/very/long/folder/ending.txt'
    expected_length = 20
    shorten = utilo.make_single(path, length=expected_length)

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
    converted = utilo.make_relative(path, root=root)
    assert converted == expected


@pytest.mark.parametrize('filename', [
    'example.yaml',
    'example',
])
def test_file_yaml(filename):
    yaml_file = utilo.yaml(filename)
    assert yaml_file == 'example.yaml'


def test_file_yaml_path_given():
    path = 'C:\\usr\\dev\\example.yaml'
    with pytest.raises(AssertionError):
        utilo.yaml(path)


@pytest.mark.parametrize('first_content, second_content, expected_result', [
    ('', '', True),
    ('A', '', False),
    ('', 'This is content', False),
    ('We are equal!\nRealy!', 'We are equal!\nRealy!', True),
])
def test_file_compare(first_content, second_content, expected_result, td):
    root = str(td)

    first = os.path.join(root, 'first')
    second = os.path.join(root, 'second')
    utilo.file_create(first, first_content)
    utilo.file_create(second, second_content)
    equals = utilo.file_compare(first, second)
    assert equals == expected_result


def test_file_compare_binary_file(td):
    root = str(td)
    utf32 = os.path.join(root, 'example.utf32')
    with open(utf32, mode='w', encoding='utf32') as fp:
        fp.write('\u1234')
    equal = utilo.file_compare(utf32, __file__)
    assert not equal


def test_file_compare_not_exists():
    first = '/c/data/abc.text'
    second = __file__
    equals = utilo.file_compare(first, second)
    assert not equals
    equals = utilo.file_compare(first=second, second=first)
    assert not equals


def test_file_lock(td):
    root = str(td)
    first = os.path.join(root, 'locked.abc')
    utilo.file_create(first, 'file to lock')
    assert not utilo.file_islocked(first)
    utilo.file_lock(first)
    assert utilo.file_islocked(first)
    # test write protection
    with pytest.raises(PermissionError):
        utilo.file_remove(first)
    assert os.path.exists(first)
    utilo.file_unlock(first)
    assert not utilo.file_islocked(first)
    utilo.file_remove(first)
    assert not os.path.exists(first), 'write protection is already there'


@pytest.mark.parametrize('path, expected', [
    ('www/helmut/test.py', 'www.helmut.test'),
    ('www\\helmut\\test.py', 'www.helmut.test'),
    ('abc\\www\\nbc', 'abc.www.nbc'),
])
def test_file_make_package(path, expected):
    result = utilo.make_package(path)

    assert result == expected, str(result)


def test_file_make_package_root():
    path = 'www/helmut/test.py'
    expected = 'helmut.test'

    result = utilo.make_package(path, root='www')

    assert result == expected, str(result)


def test_file_copy_single_file(td):
    root = str(td)
    source = os.path.join(root, 'source')
    dest = os.path.join(root, 'destination')
    os.makedirs(source)
    os.makedirs(dest)

    sourcefile = os.path.join(source, 'hello')
    utilo.file_create(sourcefile)

    utilo.file_copy(sourcefile, dest)
    assert os.path.exists(os.path.join(dest, 'hello'))


def test_file_copy_content_mult(td):
    td.mkdir('source')
    utilo.file_create('source/groupme__selm.yaml')
    utilo.file_create('source/rawmaker__helm.yaml')
    td.mkdir('dest')
    utilo.copy_content(
        'source',
        'dest',
        pattern='(rawmaker|groupme)__*.yaml',
        recursive=True,
        verbose=True,
    )
    assert os.path.exists('dest/groupme__selm.yaml')
    assert os.path.exists('dest/rawmaker__helm.yaml')


def test_file_copy_content_verbose_ignore(td):
    td.mkdir('src')
    utilo.file_create('src/groupme__selm.yaml')
    utilo.file_create('src/rawmaker__helm.yaml')
    td.mkdir('dst')
    utilo.copy_content(
        'src',
        'dst',
        pattern='(rawmaker|groupme)__*.yaml',
        recursive=True,
        verbose=True,
        ignore=lambda x: 'groupme' in x,
    )
    assert utilo.file_count(td.tmpdir.join('dst')) == 1


def test_file_count(tmpdir):
    assert not utilo.file_count(tmpdir)

    with utilo.chdir(tmpdir):
        utilo.file_create('hi.yaml')
        utilo.file_create('hi.txt')

    assert utilo.file_count(tmpdir, ext='yaml') == 1
    assert utilo.file_count(tmpdir) == 2


def test_file_tmpdir():
    create = utilo.tmpdir(utilo.ROOT)
    assert os.path.exists(create), create


def test_file_replace_binary(tmpdir):
    path = os.path.join(tmpdir, 'file.hex')
    utilo.file_replace_binary(path, b'Helm')
    # replace content
    utilo.file_replace_binary(path, b'Helm2')
    # do nothing
    utilo.file_replace_binary(path, b'Helm2')


def test_file_list():
    files = utilo.file_list(utilo.ROOT)
    assert files

    txt = utilo.file_list(utilo.ROOT, include='txt')
    assert len(txt) <= len(files)

    py = utilo.file_list(utilo.ROOT, include='py')  # pylint:disable=C0103
    assert len(py) > len(txt)

    py_txt = utilo.file_list(utilo.ROOT, include=['py', 'txt'])
    assert len(py_txt) == (len(txt) + len(py))

    exclude_txt = utilo.file_list(utilo.ROOT, exclude='txt')
    assert len(exclude_txt) == (len(files) - len(txt))


def test_file_list_relative(td):
    utilo.file_create('test.txt')
    files = utilo.file_list(td.tmpdir)
    assert files == ['test.txt']
    files = utilo.file_list(td.tmpdir, absolute=True)
    assert files != ['test.txt']


def test_make_tmpdir():
    with utilo.make_tmpdir(utilo.ROOT) as tmp_dir:
        assert os.path.exists(tmp_dir)
    assert os.path.exists(tmp_dir)


def test_make_tmpdir_remove():
    with utilo.make_tmpdir(utilo.ROOT, remove=True) as tmp_dir:
        assert os.path.exists(tmp_dir)
        os.makedirs(os.path.join(tmp_dir, 'recursive_path'))
        utilo.file_create(os.path.join(tmp_dir, 'helm.txt'))
    assert not os.path.exists(tmp_dir), tmp_dir


@pytest.mark.skip(reason='no PermissionError on linux')
def test_inform_file_permission(tmpdir, capsys):
    path = tmpdir.join('locked')
    utilo.file_create(path)
    utilo.file_lock(path)
    assert utilo.file_islocked(path)
    with pytest.raises(PermissionError, match='Permission denied'):
        utilo.file_append(path, content='data')
    assert 'HINT: Ensure that' in utilatest.stderr(capsys)
