import contextlib
import functools
import glob
import importlib
import inspect
import os
import subprocess  # nosec
import sys

import pytest

import utilo


def stderr(capsys) -> str:
    if isinstance(capsys, subprocess.CompletedProcess):
        return capsys.stderr
    return capsys.readouterr().err


def stdout(capsys) -> str:
    if isinstance(capsys, subprocess.CompletedProcess):
        return capsys.stdout
    return capsys.readouterr().out


def run(
    cmd: str,
    cwd: str = None,
    env: dict = None,
    expect: bool = True,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """Run external process.

    Args:
        cmd(str): command to run
        cwd(str): current working directory
        env(dict): modify environment variable for test run. If nothing is
                   passed, the global environment variable is used.
        expect(bool): if True: fail on error
                      if False: fail on success
                      if None: return completed process
        verbose(bool): log executed command and location
    Returns:
        Completed process.
    """
    cwd = cwd if cwd else os.getcwd()
    assert os.path.exists(cwd)
    msg = f'cwd {cwd} is not a valid directory'
    assert os.path.isdir(cwd), msg
    env = os.environ if env is None else env
    if verbose:
        utilo.log(f'cd {cwd}')
        utilo.log(cmd)
    # run process
    completed = subprocess.run(  # nosec, pylint:disable=subprocess-run-check
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
    if expect is False:  # pylint:disable=C2001
        assert_failure(completed)
    return completed


@utilo.rename(monkeypatch='mp', success='expect')
def run_cov(
    cmd: str,
    process: str,
    main: callable,
    expect: bool,
    mp,
) -> int:
    """Run `main` with `cmd`.

    Args:
        cmd(str): command to run
        process(str): name of executed tool
        main(callable): method to run
        expect(bool): expectation that process succeeds or fails,
                      use None to skip check
        mp(fixture): pytest patch/mp feature
    Returns:
        Return code of completed process.
    """
    with contextlib.suppress(AttributeError):
        cmd = cmd.split()
    assert callable(main), str(main)
    with mp.context() as context:
        # process is removed as first argument
        context.setattr(sys, 'argv', [process] + cmd)
        with pytest.raises(SystemExit) as result:
            main()
    code = utilo.returncode(result)
    assert (code == utilo.SUCCESS) == expect or expect is None, str(result)
    return code


@contextlib.contextmanager
def assert_run(command: str, cwd: str = None):
    done = utilo.run(command, cwd)
    assert done.returncode == utilo.SUCCESS, f'{done.stderr}\n{done.stdout}'
    yield done


@contextlib.contextmanager
def assert_run_fail(command: str, cwd: str = None):
    done = utilo.run(command, cwd, expect=False)
    assert done.returncode, f'{done.stderr}\n{done.stdout}'
    yield done


def single_execution() -> bool:
    """Check that test method is executed as single test.

    You can use this method to open the result in a web browser if test is
    executed with a human in front of the machine e.g. as a single test.

    >>> single_execution()
    False
    """
    frame = inspect.currentframe()
    caller = [item.function for item in inspect.getouterframes(frame)[0:9]]
    return any(item in sys.argv for item in caller)


def assert_success(process: subprocess.CompletedProcess):
    """Ensure that `process` completed correctly.

    If not a formatted information is logged
    """
    assert process, str(process)
    assert process.returncode == utilo.SUCCESS, utilo.format_completed(process)


def assert_failure(process: subprocess.CompletedProcess):
    """Ensure that `process` fails.

    If process completed correctly, a formatted information is logged.
    """
    assert process, str(process)
    assert process.returncode != utilo.SUCCESS, utilo.format_completed(process)


def create_cli_runner(package) -> '[typing.Callable, typing.Callable]':
    importlib.import_module(f'{package.__name__}.cli')
    main: callable = package.cli.main
    process: str = package.PROCESS
    # success
    success = functools.partial(
        run_cov,
        main=main,
        process=process,
        expect=True,
    )
    # failure
    failure = functools.partial(
        run_cov,
        main=main,
        process=process,
        expect=False,
    )
    return success, failure

VIRTUAL_ENVKEY = 'VIRTUAL'
VIRTUAL = VIRTUAL_ENVKEY in os.environ
NONVIRTUAL = not VIRTUAL

FAST = 'FAST' in os.environ
NIGHTLY = 'NIGHTLY' in os.environ
LONGRUN = 'LONGRUN' in os.environ or NIGHTLY
MONDAY = 'MONDAY' in os.environ
FASTRUN = FAST and not NIGHTLY and not MONDAY

VIRTUAL_REASON = 'require venv'
NONVIRTUAL_REASON = 'require non-venv'
MONDAY_REASON = 'its not monday'

WIN = 'win' in sys.platform
LIN = not WIN
COV = 'coverage' in sys.modules

# pylint: disable=invalid-name
monday = pytest.mark.skipif(not MONDAY, reason=MONDAY_REASON)
nonvirtual = pytest.mark.skipif(NONVIRTUAL, reason=VIRTUAL_REASON)
virtual = pytest.mark.skipif(VIRTUAL, reason=NONVIRTUAL_REASON)


def hasprog(prog, msg=''):
    if not msg:
        msg = f'install {prog}'
    has = pytest.mark.skipif(
        not utilo.hasprog(prog),
        reason=msg,
    )
    return has


hasgit = hasprog('git')
hasbaw = hasprog('baw')

linux = pytest.mark.skipif(not LIN, reason='linux only')
win = pytest.mark.skipif(not WIN, reason='windows only')
no_win = pytest.mark.skipif(WIN, reason='no windows')
no_linux = pytest.mark.skipif(LIN, reason='no linux')
no_cov = pytest.mark.skipif(COV, reason='skip on cov run')


def register_marker(name: str):
    """After upgrading pytest, markers must be registered in pytest
    config. To avoid putting holyvalue markers in every pytest.ini we
    bypass them by directly acessing the pytest API. This may fail in
    the future."""
    pytest.mark._markers.add(name)  # pylint:disable=W0212
    return getattr(pytest.mark, name)


longrun = register_marker('longrun')
nightly = register_marker('nightly')

# mark tests to optimize holy value parameters
# old: holyvalue = pytest.mark.holyvalue
holyvalue = register_marker('holyvalue')
displayed = register_marker('displayed')
# TODO: SUPPORT holyvalue('rawmaker.features.text.MAX_WIDTH')


# def requires(resource, folder=None):
#     exists = _exists(resource, folder)
#     if utila.iterable(resource):  # pylint:disable=W0160
#         resource = [utila.forward_slash(item) for item in resource]
#     else:
#         resource = utila.forward_slash(resource)
#     marker = pytest.mark.skipif(
#         not exists,
#         reason=f'require/generated: {resource}; folder: {folder}',
#     )
#     return marker


# def fixture_requires(resource, folder=None):
#     if _exists(resource, folder):
#         return
#     if utila.iterable(resource):  # pylint:disable=W0160
#         resource = [utila.forward_slash(item) for item in resource]
#     else:
#         resource = utila.forward_slash(resource)
#     pytest.skip(f'require/generated: {resource}; folder: {folder}')


# def _exists(resource, folder=None):
#     if utila.iterable(resource):
#         return all(_exists(item, folder=folder) for item in resource)
#     exists = os.path.exists(resinf.link(resource, folder=folder))
#     # non generated resources
#     import power  # pylint:disable=import-outside-toplevel
#     exists |= os.path.exists(resource) and resource not in power.RESOURCES
#     return exists


def step(source, pages: tuple = None, reason=None, marks=None, ids=None):
    if ids is None:
        ids = utilo.file_name(source)
    if reason:
        if marks:
            # fail = pytest.mark.xfail(reason=reason)
            assert 0, 'not implemented yet'
        else:
            marks = pytest.mark.xfail(reason=reason)
    if marks:  # pylint:disable=W0160
        result = pytest.param(source, pages, marks=marks, id=ids)
    else:
        result = pytest.param(source, pages, id=ids)
    return result
def simplify_testfile_names(files, ext='pdf', sort: bool = True) -> tuple:
    """Make path relative, remove folder structure due replacing `/`
    with `_` and remove selected file extention `ext`.

    >>> simplify_testfile_names(('/c/abc/www/second.pdf', '/c/abc/def/first.pdf'))
    ('def_first', 'www_second')

    Determine relative files against an resource folder:

    >>> simplify_testfile_names(('/c/abc', '/c/abc/def/first.pdf'))
    ('def_first',)
    """
    # ensure to compute prefix correctly
    assert len(set(files)) > 1, 'require at least two unique items.'
    assert isinstance(files, (list, tuple)), f'unsupported type: {type(files)}'
    files = [utilo.forward_slash(item) for item in files]
    prefix = utilo.forward_slash(os.path.commonpath(files))
    # remove prefix
    files = [item.replace(prefix, '') for item in files]
    # remove empty path
    files = [item for item in files if item]
    # remove first slash
    files = [item[1:] if item[0] == '/' else item for item in files]
    # remove extension
    files = [item.replace(f'.{ext}', '') for item in files]
    # simplify name
    files = [item.replace('/', '_') for item in files]
    if sort:
        files = utilo.files_sort(files)
    return tuple(files)


@contextlib.contextmanager
def increased_filecount(
    path: str = None,
    ext: str = None,
    mindiff: int = None,
    maxdiff: int = None,
):
    """Ensure that some files were created while yielded operation.

    Args:
        path(str): path to check for file creation, if path is None use cwd
        ext(str): look for a special file extention
        mindiff(int): minimal number of created files, if None: 1 is used
        maxdiff(int): maximal number of created files, if None: utila.INF is used
    Raises:
        AssertionError: if to few or less files are created
    Yields:
        None: to run file creation operation
    """
    if path is None:
        path = os.getcwd()
    utilo.exists_assert(path)
    assert mindiff is None or mindiff >= 0, str(mindiff)
    assert maxdiff is None or maxdiff >= 0, str(maxdiff)
    pattern = '**/*.*' if ext is None else f'**/*.{ext}'
    path = utilo.forward_slash(str(path), newline=False)
    pattern = f'{path}/{pattern}'
    before = list(glob.glob(pattern, recursive=True))
    yield
    after = list(glob.glob(pattern, recursive=True))
    mindiff = 1 if mindiff is None else mindiff
    maxdiff = utilo.INF if maxdiff is None else maxdiff
    current = len(after) - len(before)
    assert mindiff <= current <= maxdiff, (
        f'mindiff: {mindiff} <= {current} <= maxdiff: {maxdiff}\n'
        f'{before}\n\n{after}')


@pytest.fixture
def mp(monkeypatch):
    return monkeypatch


@pytest.fixture
def td(testdir):
    return testdir
