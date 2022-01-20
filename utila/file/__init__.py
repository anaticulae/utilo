#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""File
====

TODO: add tmp, path, verify/validate module

"""

import contextlib
import glob
import os
import random
import shutil
import stat
import sys

import utila
import utila.file.securewrapper

# width of tempfile name
MAX_NUMBER = 32
SHARED_TMP = 'SHARED_TMP'


def tmp(root) -> str:
    """Return path to temporary folder. If not exists, create folder

    To redirect the temp base, define `KIWI_TEMPBASE` as a global
    environment variable. The temp folder is created in this folder
    under the name of the given project, defined in `root` variable.

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root, str(root)
    # redirect temp folder to central folder, defined in `SHARED_TMP`. we
    # need control about temp folder. Temp folder must not exist in
    # site-packages, so `SHARED_TMP` is required.
    projectname = os.path.split(root)[1]
    # queuemo-1.17.2-py3.8.egg
    projectname = projectname.split('-', maxsplit=1)[0]
    try:
        path = os.path.join(os.environ[SHARED_TMP], projectname)
    except KeyError:
        utila.error('DEFINE $SHARED_TMP')
        sys.exit(utila.FAILURE)
    os.makedirs(path, exist_ok=True)
    return path


def file_append(path: str, content: str, create: bool = False, private: bool = False): # yapf:disable
    """Append `content` to file given in `path`.

    Args:
        path(str): file to write
        content(str): write content to file
        create(bool): if True, create File if not exists
        private(bool): if True, use encryption
    Hint:
        If file not exists and create == False, an assertion is fired.
    """
    assert create or os.path.exists(path), str(path)
    if not os.path.exists(path):
        file_create(path, content, private=private)
        return
    with utila.file.securewrapper.open(
            path,
            mode='a',
            newline=utila.NL,
            encoding=utila.U8,
            private=private,
    ) as fp:
        fp.write(content)


def file_create(path: str, content: str = '', private: bool = False):
    """Create file `path` with the content `content`

    Args:
        path(str): path to write file, path must not exists
        content(str): content to write in given `path`
        private(bool): if True, use encryption
    Hint:
        If file exists, an assertion is raised.
    """
    parent = utila.path_parent(path)
    assert os.path.exists(parent) or not parent, f'{parent} does not exists'
    assert not os.path.exists(path), f'{path} already exists'
    with utila.file.securewrapper.open(
            path,
            mode='w',
            newline=utila.NL,
            encoding=utila.U8,
            private=private,
    ) as fp:
        fp.write(content)


def file_create_tmp(
    content: str = '',
    root: str = None,
    private: bool = False,
) -> str:
    """Create file `content` in a temporary file

    Args:
        content(str): content to write in given `path`
        root(str): project root to create temporary file
        private(bool): if True, use encryption
    Returns:
        path to temporary file

    >>> assert file_create_tmp('temporary content', utila.ROOT)
    """
    path = tmpfile(root)
    with utila.file.securewrapper.open(
            path,
            mode='w',
            newline=utila.NEWLINE,
            encoding=utila.UTF8,
            private=private,
    ) as fp:
        fp.write(content)
    return path


def file_create_binary(path: str, content: bytes = b'', private: bool = False):
    """Create file `path` with the content `content`

    Args:
        path(str): path to write file, path must not exists
        content(str): content to write in given `path`
        private(bool): if True, use encryption
    Hint:
        If file already exists, an assertion is raised.
    """
    parent = utila.path_parent(path)
    assert os.path.exists(parent) or not parent, f'{parent} does not exists'
    assert not os.path.exists(path), f'{path} already exists'
    with utila.file.securewrapper.open(path, mode='wb', private=private) as fp:
        fp.write(content)


def file_read(path: str, size: int = -1, private: bool = False):
    utila.exists_assert(path)
    with utila.file.securewrapper.open(
            path,
            mode='r',
            newline=utila.NL,
            encoding=utila.U8,
            private=private,
    ) as fp:
        return fp.read(size)


def file_read_binary(path: str, size: int = -1, private: bool = False) -> bytes:
    """Read binary file content"""
    utila.exists_assert(path)
    with utila.file.securewrapper.open(path, mode='rb', private=private) as fp:
        content = fp.read(size)
    return content


def file_remove(path: str):
    utila.exists_assert(path)
    assert os.path.isfile(path), path
    os.remove(path)


def file_replace(path: str, content: str, private: bool = False):
    """Replace file content.

    Args:
        path(str): path to file
        content(str): content to write
        private(bool): if True, use encryption

    1. If not exit, create file
    2. If exists,   compare content, if changed than replace
                                     if not, do nothing
    """
    if not os.path.exists(path):
        file_create(path, content, private=private)
        return
    current_content = file_read(path, private=private)
    if current_content == content:
        return

    with utila.file.securewrapper.open(
            path,
            mode='w',
            newline=utila.NL,
            encoding=utila.U8,
            private=private,
    ) as fp:
        fp.write(content)


def file_replace_binary(path: str, content: bytes, private: bool = False):
    """Replace file content.

    Args:
        path(str): path to file
        content(str): content to write
        private(bool): if True, use encryption

    1. If not exist, create file
    2. If exists,   compare content, if changed than replace
                                     if not, do nothing
    """
    if not os.path.exists(path):
        file_create_binary(path, content, private=private)
        return
    current_content = file_read_binary(path, private=private)
    if current_content == content:
        return

    with utila.file.securewrapper.open(path, mode='wb', private=private) as fp:
        fp.write(content)


def file_compare(first: str, second: str) -> bool:
    """Compare the content of `first` and `second`

    If least one file not exists, there are not equal

    Args:
        first(str): path to first file
        second(str): path to second file
    Returns:
        True if paths exists and hashed content is equal else False.
    """
    if not os.path.isfile(first):
        return False
    if not os.path.isfile(second):
        return False
    first = hash(file_read_binary(first))
    second = hash(file_read_binary(second))
    return first == second


def file_lock(path: str):
    """Protect file `path` with write protection.

    Before locking check that file exists and no lock is already set. If file
    not exists or a file lock is already set, `AssertError` is raised.

    Args:
        path(str): path to protect
    Raises:
        AssertionError
    """
    # set read only
    assert os.path.exists(path), f'{path} does not exists'
    assert not file_islocked(path), 'file is already locked'
    os.chmod(path, mode=stat.S_IREAD)


def file_unlock(path: str):
    """Remove write protection of file `path`.

    Before unlock check that file exists and lock protection is set. If
    file not exists or a file lock is not set, `AssertError` is raised.

    Args:
        path(str): path to unprotect
    Raises:
        AssertionError
    """
    assert os.path.exists(path), f'{path} does not exists'
    assert file_islocked(path), 'file is not locked'
    os.chmod(path, mode=stat.S_IWRITE)


def file_islocked(path: str):
    """Check if write protection is set. If `path` does not exists,
    AssertionError is raised."""
    assert os.path.exists(path), f'{path} does not exists'
    return not os.access(path, os.W_OK)


def file_copy(
    src: str = None,
    dst: str = None,
    update: bool = True,
    exception: bool = False,
    timestamp: bool = True,
    private: bool = False,
    **kwargs,
):
    """Copy a single `src` file to `dst` file or folder.

    Args:
        src(str): path to existing source file
        dst(str): a folder or a file to copy
        update(bool): copy only when the source file is different than
                      the dst file or when the dst file is missing.
        exception(bool): if True  raise exception if copying is not possible
                         if False log error and raise exit
        timestamp(bool): if True, copy timestamp
        private(bool): encrypt data
        kwargs(dict): backward compatible
    Raises:
        OSError: if coping is not possible and exception is True
        SameFileError: if src and dst is equal
    """
    if kwargs.get('source', None):
        import warnings
        warnings.warn('use file_copy(src=) instead of source')
        src = kwargs['source']
    if kwargs.get('destination', None):
        import warnings
        warnings.warn('use file_copy(dst=) instead of source')
        dst = kwargs['destination']
    assert os.path.exists(src), f'"{src}" does not exists'
    try:
        if os.path.exists(dst) and not utila.isfilepath(dst):
            # use name of current file as new file name
            # TODO: IS THIS REALLY NECESSARY?
            dst = os.path.join(dst, utila.path_current(src))
        if update and file_compare(src, dst):
            # file is up to date
            return
        parent = utila.path_parent(dst)
        os.makedirs(parent, exist_ok=True)
        # shutil.copy
        utila.file.securewrapper.copy(src, dst, private=private)
        if timestamp:
            filetime = utila.file_age(src)
            utila.file_age_update(dst, filetime)
    except OSError as error:
        utila.error(f'could not overwrite: {dst}')
        if exception:
            raise error
        sys.exit(utila.FAILURE)


def file_count(path: str, ext: str = None, recursive: bool = True) -> int:
    utila.exists_assert(path)
    pattern = f'{path}/**/*.*' if ext is None else f'{path}/**/*.{ext}'
    collected = list(glob.glob(pattern, recursive=recursive))
    return len(collected)


def file_list(
    path: str,
    include: list = None,
    exclude: list = None,
    recursive: bool = True,
    absolute: bool = False,
) -> list:
    """Scans `path` recursively and returns list of relative file path
    which matches `include` or `exclude` pattern.

    Args:
        path(str): root path to scan files
        include(list): list of patterns to include
        exclude(list): list of patterns to exclude
        recursive(bool): visit child folder
        absolute(bool): if True add `path` to extracted files
    Returns:
        List of selected files.
    """
    utila.exists_assert(path)
    msg = f'only one pattern is allowed {include} ! {exclude}'
    assert not (include and exclude), msg
    include = include if include else []
    exclude = exclude if exclude else []
    include = [include] if isinstance(include, str) else include
    exclude = [exclude] if isinstance(exclude, str) else exclude
    # make unique and ?fast?
    include: set = set(include)
    exclude: set = set(exclude)
    result = []
    for item in glob.glob(f'{path}/**/*', recursive=recursive):
        if not os.path.isfile(item):
            continue
        item = os.path.relpath(item, path)
        filepath = utila.forward_slash(item)
        try:
            ext = filepath.rsplit('.', maxsplit=1)[1]
        except IndexError:
            # file without extension
            ext = None
        if include:
            if ext not in include:
                continue
        if exclude:
            if ext in exclude:
                continue
        if absolute:
            filepath = os.path.join(path, item)
        result.append(filepath)
    return result


def file_name(path: str, ext: bool = False) -> str:
    """Determine file name without file extension out of file path.

    >>> file_name('/etc/profile.d/helm.sh')
    'helm'
    >>> file_name('info.txt')
    'info'
    >>> file_name('/etc/.tmp')
    '.tmp'
    >>> file_name('.etc')
    '.etc'
    >>> file_name('/no/file/ext')
    'ext'
    >>> file_name('etc/dev/raw.png', ext=True)
    'raw.png'
    """
    assert path
    path = utila.forward_slash(path)
    try:
        _, name = path.rsplit('/', 1)
    except ValueError:
        name = path
    if ext:
        return name
    if name[0] == '.':
        return name
    return name.split('.')[0]


def file_ext(path: str) -> str:
    """Determine file extension out of `path`. If path does not contain
    any file extension, None is returned.

    >>> file_ext('/c/images/test.bmp')
    'bmp'
    >>> file_ext('test.yaml')
    'yaml'
    >>> file_ext('.tmp') is None
    True
    >>> file_ext('/c/hekn/.tmp') is None
    True
    >>> file_ext('/no/ext/here') is None
    True
    """
    assert path
    path = utila.forward_slash(path)
    try:
        _, name = path.rsplit('/', 1)
    except ValueError:
        name = path
    if name[0] == '.':
        # .tmp
        return None
    try:
        return name.split('.')[1]
    except IndexError:
        return None


def files_sort(files: list) -> list:
    """Sort `files` path alphabetically. Sort file names by number if given.

    >>> files_sort(('/c/a', '/c/200.txt', '/c/2.txt', '/c/3', '/c/0.bmp'))
    ['/c/0.bmp', '/c/2.txt', '/c/3', '/c/200.txt', '/c/a']
    """
    files = [utila.forward_slash(item) for item in files]

    def number_filename(item):
        # sort file names if they are numbers: 0,1,2,3,4,5,6,7,8,9,10
        item = item.lower()
        item = file_name(item)
        with contextlib.suppress(ValueError):
            # sort items by number
            item = int(item)
            # ensure to compare str and str and not str and int
            item = str(item).zfill(20)
        return item

    files = sorted(files, key=number_filename)
    return files


# Alphabetic with Nn and Tt to avoid \n\t in connex with file names
POOL = 'ABCDEFGHIJKLMOPQRSUVYXYZabcdefghijklmtpqrsuvyxyz123456789'


def tmpname(width: int = MAX_NUMBER) -> str:
    """Get random file-name with 20-ziffre, random name.

    >>> len(tmpname(13)) == 13
    True

    Args:
        width(int): length of tmpname
    Returns:
        filename(str): random file name
    """
    assert width >= 1
    choises = random.sample(POOL, width)
    result = ''.join(choises)
    return result


def tmpfile(root):
    """Get temporary file-path located in root or `TMPDIR` as default.

    Returns:
        filepath(str): to tempfile in TMPDIR
    """
    assert root is None or os.path.exists(root)
    tmpfolder = tmp(root)
    name = tmpname()
    path = os.path.join(tmpfolder, name)
    if os.path.exists(path):
        # try again to find unused temp file
        return tmpfile(root)
    return path


def tmpdir(root, create: bool = True, trys: int = 10):
    """Get temporary directory-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert trys, trys
    utila.exists_assert(root)
    tmppath, name = tmp(root), tmpname()
    path = os.path.join(tmppath, name)
    if os.path.exists(path):
        # try again to find unused tmp dir
        return tmpdir(root, create=create, trys=trys - 1)
    if create:
        try:
            os.makedirs(path)
        except OSError:
            return tmpdir(root, create=create, trys=trys - 1)
    # ease for the developer
    path = utila.forward_slash(path)
    return path


@contextlib.contextmanager
def make_tmpdir(root: str, remove: bool = False, max_file_guard=100):
    """\
    root: project root as backup for temporary path. This path will be
    used if SHARED_TMP does not exists.

    Yields:
        str: created temporary directory
    """
    utila.exists_assert(root)
    path = tmpdir(root, create=False)
    assert not os.path.exists(path), path
    os.makedirs(path)

    yield path

    if remove:
        msg = f'do you really want to remove this recursively? {path}'
        assert len(utila.file_list(path)) < max_file_guard, msg
        shutil.rmtree(path)


def make_absolute(path: str, cwd=None) -> str:
    """Convert path to absolute. If path is already absolute, do nothing.

    Args:
        path(str): relative path to convert to absolute path
        cwd(str): current working directory. If nothing is passed,
                  os.getcwd is used.
    Returns:
        absolute path belong to current working directory
    """
    if cwd is None:
        cwd = os.getcwd()

    if not os.path.isabs(path):
        # Make path absolute
        path = os.path.join(cwd, path)
    return path


def make_relative(path: str, root: str = None) -> str:
    r"""Cut leading `root` from `path`.

    >>> make_relative('C:/folder/names/test.pdf', root='C:/folder/')
    'names/test.pdf'

    >>> make_relative('resources\\main\\examples', 'resources')
    'main/examples'

    Hint:
        Convert path to forwards slash's.
    See:
        os.path.relpath
    """
    if root is None:
        root = os.getcwd()
    root = utila.forward_slash(root)
    path = utila.forward_slash(path)

    path = path.replace(root, '')
    if path[0] == '/':
        path = path[1:]
    return path


def make_single(path: str, replacement='_', length: int = 40) -> str:
    """Convert path sequence to single str to use as folder name.

    Sometimes it is handy to shrink the path level of a folder
    hierarchy into a single flat list. This method enables to convert
    this path into a single name.

    Examples:
        C:/folder/names/test.pdf        C_folder_names_test_pdf
        resources\\main\\examples       resources_main_examples

    Args:
        path(str): conventional path
        replacement(str): char which replace detected pattern
        length(int): limit result length - count from right to left, to
                     use this if you require only short subset of
                     single-result.
    Returns:
        converted single path
    """
    path = str(path)
    finder = [
        ':/',
        ':\\',
        '/',
        '\\',
        '.',
    ]
    for pattern in finder:
        path = path.replace(pattern, replacement)
    return path[-length:]


def make_package(path: str, root: str = None) -> str:
    """Covert file path to pythonic package path.

    Args:
        path(str): file or directory path
        root(str): make `path` relative to `root`
    Returns:
        pythonic package path

    Examples:
        /groupme/words/helmut.py         groupme.words.helmut
        groupme\\words\\helmut.py        groupme.words.helmut
    """
    path = str(path)  # work with pytest path
    assert len(path) > 0, 'empty path'  # pylint:disable=len-as-condition
    if root is not None:
        root = str(root)
        path = make_relative(path, root=root)
    path = utila.forward_slash(path)
    path = path.replace('.py', '')
    path = path.replace('/', '.')
    return path


def assert_file(files, filetype: str):
    """Ensure that the given `files` have the correct `filetype`

    Args:
        files(list): list with files
        filetype(str): filetype without leading dot
    Raises:
        AssertionError: when passing invalid files
    """
    # support passing single str
    files = [files] if isinstance(files, str) else files
    # ensure passing without dot
    filetype = filetype[1:] if filetype[0] == '.' else filetype
    raises = 0
    for item in files:
        if not item.endswith('.%s' % filetype):
            utila.error('No %s file: %s' % (filetype, item))
            raises += 1
    assert not raises, 'wrong file types'


def assert_html(files):
    """Ensure that all given `files` are `html` files"""
    assert_file(files, 'html')


def assert_yaml(files):
    """Ensure that all given `files` are `yaml` files.

    >>> assert_yaml('test.yaml')
    """
    assert_file(files, 'yaml')


def assert_json(files):
    """Ensure that all given `files` are `json` files.

    >>> assert_json('test.json')

    >>> assert_json('test.html')
    Traceback (most recent call last):
      ...
    AssertionError: wrong file types
    """
    assert_file(files, 'json')


def yaml(filename: str) -> str:
    """Add `yaml` file extension if required.

    Args:
        filename(str): add `yaml` file ending if not ends with
    Returns:
        filename with .yaml ending
    """
    assert not ('/' in filename or '\\' in filename), f'bad filename {filename}'
    if not filename.endswith('.yaml'):
        filename = f'{filename}.yaml'
    return filename
