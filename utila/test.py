#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import glob
import inspect
import os
import subprocess
import sys
import webbrowser

import pytest

import utila
import utila.logger
from utila.string import fix_encoding
from utila.utils import SUCCESS

VIRTUAL_ENVKEY = 'VIRTUAL'
VIRTUAL = VIRTUAL_ENVKEY in os.environ
NONVIRTUAL = not VIRTUAL

FAST = 'FAST' in os.environ.keys()
NIGHTLY = 'NIGHTLY' in os.environ.keys()
LONGRUN = 'LONGRUN' in os.environ.keys() or NIGHTLY
FASTRUN = not LONGRUN or FAST

LONGRUN_REASON = 'test requires to much time'
VIRTUAL_REASON = 'require virtual environment'
NONVIRTUAL_REASON = 'require non virtual environment'

# pylint: disable=invalid-name
skip_longrun = pytest.mark.skipif(FASTRUN, reason=LONGRUN_REASON)
skip_nightly = pytest.mark.skipif(FASTRUN or not NIGHTLY, reason=LONGRUN_REASON)
skip_nonvirtual = pytest.mark.skipif(NONVIRTUAL, reason=VIRTUAL_REASON)
skip_virtual = pytest.mark.skipif(VIRTUAL, reason=NONVIRTUAL_REASON)


def run(
        cmd: str,
        cwd: str = None,
        env: dict = None,
        expect: bool = True,
) -> subprocess.CompletedProcess:
    """Run external process

    Args:
        cmd(str): command to run
        cwd(str): current working directory
        env(dict): modify environment variable for test run. If nothing is
                   passed, the global environment variable is used.
        expect(bool): if True: fail on error
                      if False: fail on success
                      if None: return completed process
    Returns:
        Completed process.
    """
    cwd = cwd if cwd else os.getcwd()
    assert os.path.exists(cwd)
    msg = 'cwd %s is not a valid directory' % cwd
    assert os.path.isdir(cwd), msg

    env = os.environ if env is None else env

    completed = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        errors='replace',
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    if expect is True:
        assert_success(completed)
    if expect is False:
        assert_failure(completed)
    return completed


def run_command(
        cmd: str,
        process: str,
        main: callable,
        success: bool,
        monkeypatch,
) -> int:
    """Run `main` with `command`

    Args:
        cmd(str): command to run
        process(str): name of executed tool
        main(callable): method to run
        success(bool): expectation that process succeeds or fails
        monkeypatch(fixture): pytest patch feature
    Returns:
        Return code of completed process.
    """
    with contextlib.suppress(AttributeError):
        cmd = cmd.split()
    assert callable(main), str(main)

    with monkeypatch.context() as context:
        # process is removed as first argument
        context.setattr(sys, 'argv', [process] + cmd)
        with pytest.raises(SystemExit) as result:
            main()
    code = returncode(result)
    assert (code == SUCCESS) == success, str(result)
    return code


@contextlib.contextmanager
def assert_run(command: str, cwd: str):
    completed = run(command, cwd)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode == SUCCESS, msg
    yield completed


@contextlib.contextmanager
def assert_run_fail(command: str, cwd: str):
    completed = run(command, cwd, expect=False)
    msg = '%s\n%s' % (completed.stderr, completed.stdout)
    assert completed.returncode, msg
    yield completed


def clean_install(root, package):
    uninstall = 'pip uninstall %s -y' % package
    install = 'python setup.py install'

    clean_and_run = uninstall + ' && ' + install
    completed = run(clean_and_run, cwd=root)
    assert completed.returncode == SUCCESS, completed.stdout + completed.stderr


def install_and_run(root, package, executable=None):
    """Install and run --help to ensure basic function"""
    executable = executable if executable else package
    uninstall = 'pip uninstall %s -y' % package
    install = 'python setup.py install && %s --help' % executable

    clean_and_run = uninstall + ' && ' + install
    completed = run(clean_and_run, cwd=root)
    assert completed.returncode == SUCCESS, completed.stdout + completed.stderr


def returncode(exeception: Exception) -> int:
    """Determine return code raised from exit()"""
    return int(str(exeception.value))


def assert_success(process: subprocess.CompletedProcess):
    """Ensure that `process` completed correctly, if not a formated
    information is logged"""
    assert process, str(process)
    assert process.returncode == utila.SUCCESS, utila.format_completed(process)


def assert_failure(process: subprocess.CompletedProcess):
    """Ensure that `process` fails. If process completed correctly, a
    formated information is logged."""
    assert process, str(process)
    assert process.returncode != utila.SUCCESS, utila.format_completed(process)


def log_raw(content: str):
    """Print `content` which raises an AssertError. Fix encoding if
    non-utf8 character are printed.

    Hint: Avoid using print() to reduse finding 'print' when searching
    in code base.

    Example:
        asssert len(abc) > 100, utila.log_raw(abc)
    """
    content = fix_encoding(content)
    print(content, flush=True)


def single_execution():
    """Check that test method is executed as single test. You can use
    this method to open the result in a web browser if test is executed
    with a human in front of the machine eg. as a single test."""
    utila.refactor(major=2, description='move to utila test')
    frame = inspect.currentframe()
    parent = inspect.getouterframes(frame)[1]
    caller = parent.function
    return all([item in sys.argv for item in ['-k', caller]])


@contextlib.contextmanager
def increased_filecount(
        path: str,
        ext: str = None,
        mindiff: int = None,
        maxdiff: int = None,
):
    """Ensure that some files were created while yielded operation.

    Args:
        path(str): path to check for file creation
        ext(str): look for a special file extention
        mindiff(int): minimal number of created files, if None: 1 is used
        maxdiff(int): maximal number of created files, if None: utila.INF is used
    Raises:
        AssertionError: if to few or less files are created
    Yields:
        None: to run file creation operation
    """
    assert os.path.exists(path), str(path)
    assert mindiff is None or mindiff >= 0, str(mindiff)
    assert maxdiff is None or maxdiff >= 0, str(maxdiff)
    pattern = '**/*.*' if ext is None else f'**/*.{ext}'
    with utila.chdir(path):
        before = list(glob.glob(pattern, recursive=True))
        yield
        after = list(glob.glob(pattern, recursive=True))
    mindiff = 1 if mindiff is None else mindiff
    maxdiff = utila.INF if maxdiff is None else maxdiff
    current = len(after) - len(before)
    assert mindiff <= current <= maxdiff, (
        f'mindiff: {mindiff} maxdiff: {maxdiff}\n'
        f'{before}\n\n{after}')


@contextlib.contextmanager
def open_webbrowser(path: str):
    """Open webbrowser on `give` path if test is used as single
    execution.

    Args:
        path(str): path to located html file
    Yields:
        None: to run operation to create website
    """
    yield
    assert os.path.exists(path), str(str)
    if single_execution():
        webbrowser.open(path)


def simplify_testfile_names(files, ext='pdf') -> tuple:
    """Make path relative, remove folder structure due replacing `/`
    with `_` and remove selected file extention `ext`.

    >>> simplify_testfile_names(('/c/abc/www/second.pdf', '/c/abc/def/first.pdf'))
    ('def_first', 'www_second')
    """
    files = [utila.forward_slash(item) for item in files]
    prefix = utila.forward_slash(os.path.commonpath(files))

    # remove first slash
    files = [item.replace(prefix, '')[1:] for item in files]
    files = [item.replace(f'.{ext}', '') for item in files]
    files = [item.replace('/', '_') for item in files]
    files = sorted(files, key=lambda x: x.lower())
    return tuple(files)
