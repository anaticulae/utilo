#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import glob
import os
import random
import re
import shutil
import stat

import utila
from utila.logger import error
from utila.string import forward_slash
from utila.utils import FAILURE
from utila.utils import NEWLINE
from utila.utils import TMP
from utila.utils import UTF8
from utila.utils import chdir

# width of tempfile name
MAX_NUMBER = 20
SHARED_TEMP = 'SHARED_TMP'


def tmp(root) -> str:
    """Return path to temporary folder. If not exists, create folder

    To redirect the tempbase, define `KIWI_TEMPBASE` as a global envionment
    variable. The temp folder is created in this folder under the name of the
    given project, defined in `root` variable.

    Args:
        root(str): project root
    Returns:
        path to temporary folder
    """
    assert root, str(root)
    try:
        # redirect temp folder to central folder, defined in `SHARED_TEMP`.
        # we need control about temp folder. Temp folder must not exist in
        # site-packages, so `SHARED_TEMP` is required.
        _, projectname = os.path.split(root)
        path = os.path.join(os.environ[SHARED_TEMP], projectname)
    except KeyError:
        path = os.path.join(root, TMP)
    os.makedirs(path, exist_ok=True)
    return path


def file_append(path: str, content: str, create: bool = False):
    """Append `content` to file given in `path`.

    Args:
        path(str): file to write
        content(str): write content to file
        create(bool): if True, create File if not exists

    Hint:
        If file not exists and create == False, an assertion is fired.
    """
    if not create:
        assert os.path.exists(path)
    if not os.path.exists(path):
        file_create(path, content)
    else:
        with open(path, mode='a', newline=NEWLINE, encoding=UTF8) as fp:
            fp.write(content)


def file_create(path: str, content: str = ''):
    """Create file `path` with the content `content`

    Args:
        path(str): path to write file, path must not exists
        content(str): content to write in given `path`

    Hint:
        If file exists, an assertion is raised.
    """
    parent = os.path.split(path)[0]
    assert os.path.exists(parent) or not parent, f'{parent} does not exists'
    assert not os.path.exists(path), f'{path} already exists'
    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def file_read(path: str):
    assert os.path.exists(path), path
    with open(path, mode='r', newline=NEWLINE, encoding=UTF8) as fp:
        return fp.read()


def file_read_binary(path: str) -> bytes:
    """Read binary file content"""
    assert os.path.exists(path), path
    with open(path, mode='rb') as fp:
        content = fp.read()
    return content


def file_remove(path: str):
    assert os.path.exists(path), path
    assert os.path.isfile(path), path
    os.remove(path)


def file_replace(path: str, content: str):
    """Replace file content

    1. If not exit, create file
    2. If exists,   compare content, if changed than replace
                                     if not, do nothing
    Args:
        path(str): path to file
        content(str): content to write
    """
    if not os.path.exists(path):
        file_create(path, content)
        return
    current_content = file_read(path)
    if current_content == content:
        return

    with open(path, mode='w', newline=NEWLINE, encoding=UTF8) as fp:
        fp.write(content)


def file_compare(first: str, second: str) -> bool:
    """Compare the content of `first` and `second`

    If least one file not exists, there are not eqaul

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
        source: str,
        destination: str,
        update: bool = True,
):
    """Copy a single `source` file to `destination` file or folder.

    Args:
        source(str): path to existing source file
        destination(str): a folder or a file to copy
        update(bool): copy only when the source file is different than
                      the destination file or when the destination file
                      is missing.
    """
    assert os.path.exists(source), f'"{source}" does not exists'
    try:
        if update and file_compare(source, destination):
            return
        parent, _ = os.path.split(destination)
        os.makedirs(parent, exist_ok=True)
        shutil.copy(source, destination)
    except OSError:
        error(f'could not overwrite: {destination}')
        exit(FAILURE)


def file_count(path: str, ext: str = None, recursive: bool = True) -> int:
    assert os.path.exists(path), path
    pattern = '**/*.*' if ext is None else f'**/*.{ext}'
    with utila.chdir(path):
        collected = list(glob.glob(pattern, recursive=recursive))
    return len(collected)


def isfilepath(path: str) -> bool:
    """Check that given `path` is a file path.

    >>> isfilepath('/c/tmp/file.txt')
    True
    >>> isfilepath('/c/tmp/.tmp')
    False
    """
    assert path, path
    if os.path.exists(path):
        return os.path.isfile(path)
    base = os.path.basename(path)
    if base[0] == '.':
        # .tmp
        return False
    return '.' in base


def copy_content(  # pylint:disable=R1260
        source: str,
        destination: str,
        pattern: str = None,
        *,
        recursive: bool = False,
        update: bool = False,
        verbose: bool = False,
):
    """Copy the content from `source` to `destination` folder. If
    `destination` folder does not exists, it will be created.

    Pattern-Syntax:
        In the current implementation only one multiple field is
        possible. The multiple pattern group is inside brackets and is
        separated by |. For example: (rawmaker|groupme)__*.yaml, copies
        rawmaker and groupme yaml files.

    Hint:
        Why not using shutil.copytree?: Copy tree expect that
        destination does not exists, but we need this.

    Args:
        source(str): file or directory to copy
        destination(str): directory to copy source item(s)
        pattern(str): accept files which matches this pattern, if None
                      all files matches.

        recursive(bool): if True, copy child folder
        update(bool): move only when the source file is newer than the
                      destination file or when the destination file is
                      missing.
        verbose(bool): explain what is being done
    """
    if os.path.isfile(source):
        if not isfilepath(destination):
            destination = os.path.join(destination, os.path.basename(source))
        if verbose:
            utila.log(f'cp: {source} -> {destination}')
        file_copy(
            source,
            destination,
            update=update,
        )
        return

    if pattern is None:
        pattern = '*'

    multiple = split_multipattern(pattern)
    if multiple:
        if verbose:
            utila.log(f'split pattern: {pattern} -> {multiple}')
        for converted_pattern in multiple:
            # run multiple operation
            copy_content(
                source,
                destination,
                pattern=converted_pattern,
                recursive=recursive,
                update=update,
                verbose=verbose,
            )
        return

    pattern = f'**/{pattern}' if recursive else pattern

    with chdir(source):
        selected = list(glob.glob(pattern, recursive=recursive))

    for item in selected:
        source_ = os.path.join(source, item)
        dest_ = os.path.join(destination, item)
        if os.path.isfile(source_):
            if verbose:
                utila.log(f'cp: {source_} -> {dest_}')
            file_copy(source_, dest_, update=update)
        else:
            if verbose:
                utila.log(f'mkdir: {dest_}')
            os.makedirs(dest_, exist_ok=True)


def split_multipattern(multipattern):
    """Split multiple pattern into several single pattern.

    >>> split_multipattern('(rawmaker|groupme)__*.yaml')
    ['rawmaker__*.yaml', 'groupme__*.yaml']
    """
    # TODO: SUPPORT MULTIPLE GROUPS
    pattern = r'\([\w|\|\_\-]+\)'
    matched = re.match(pattern, multipattern)
    if not matched:
        return None
    match = utila.regex.extract_match(matched)
    result = []
    without_brackets = match[1:-1]
    for item in without_brackets.split('|'):
        result.append(multipattern.replace(match, item))
    return result


def from_raw_or_path(
        content: str,
        ftype: str = 'yaml',
        fname: str = None,
) -> str:
    """Provide raw content from file or pass content

    This method enables the interface to get content from filepath,
    directory or use direct raw content.

    Args:
        content(str): filepath or raw content
        ftype(str): file type which is checked
        fname(str): if `content` is directory, and ``directory/fname.ftype``
                    exists, load ``directory/fname.ftype``
    Returns:
        loaded content or raw passed content
    Raises:
        FileNotFoundError: if `content` path not exists
    """
    content = str(content)  # convert `LocalPath` to str
    if content.endswith(f'.{ftype}') and not os.path.exists(content):
        raise FileNotFoundError(f'file not exists: {content}')
    try:
        isdir = utila.NEWLINE not in content and os.path.isdir(content)
    except ValueError:
        # File name is to long, cause testing yaml content as file content.
        isdir = False
    if fname and isdir:
        # use default file path if exists
        newpath = os.path.join(content, f'{fname}.{ftype}')
        if os.path.exists(newpath):
            content = newpath
        else:
            raise FileNotFoundError(f'directory not found: {newpath}')
    # filepath must not have any linebreaks
    if len(content.splitlines()) == 1 and os.path.isfile(content):
        content = file_read(content)
    return content


def tmpname(width: int = MAX_NUMBER) -> str:
    """Get random file-name with 20-ziffre, random name.

    Args:
        width(int): length of tmpname
    Returns:
        filename(str): random file name
    """
    assert width
    max_test_number = 10**width

    return str(random.randrange(max_test_number)).zfill(width)


def tmpfile(root):
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert os.path.exists(root)
    tmppath = tmp(root)

    name = 'tmp%s' % tmpname()
    path = os.path.join(tmppath, name)
    if os.path.exists(path):
        # try again to find unused temp file
        return tmpfile(root)
    return path


def tmpdir(root, create: bool = True, trys: int = 10):
    """Get temporary directory-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    assert os.path.exists(root)
    assert trys, trys
    tmppath = tmp(root)

    name = 'tmp%s' % tmpname()
    path = os.path.join(tmppath, name)
    if os.path.exists(path):
        # try again to find unused tmp dir
        return tmpfile(root)
    if create:
        try:
            os.makedirs(path)
        except OSError:
            return tmpdir(root, create=create, trys=trys - 1)
    return path


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
        Convert path to forwards slashs.
    See:
        os.path.relpath
    """
    if root is None:
        root = os.getcwd()
    root = forward_slash(root, save_newline=False)
    path = forward_slash(path, save_newline=False)

    path = path.replace(root, '')
    if path[0] == '/':
        path = path[1:]
    return path


def make_single(path: str, replacement='_', length: int = 40) -> str:
    """Convert path sequence to single str which can be used as folder name.

    Sometimes it is handy to shrink the path level of a folder
    hierarchie into a single flat list. This method enables to convert
    this path into a single name which can be used to reach this goal.

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
    path = forward_slash(path, save_newline=False)
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
            error('No %s file: %s' % (filetype, item))
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
    """Add `yaml` file extention if required.

    Args:
        filename(str): add `yaml` file ending if not ends with
    Returns:
        filename with .yaml ending
    """
    assert not ('/' in filename or '\\' in filename), f'bad filename {filename}'
    if not filename.endswith('.yaml'):
        filename = f'{filename}.yaml'
    return filename
