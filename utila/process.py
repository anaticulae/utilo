# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import contextlib
import copy
import dataclasses
import functools
import inspect
import os
import subprocess  # nosec
import sys
import threading

import utila
import utila.utils


def run(
    cmd: str,
    cwd: str = None,
    env: dict = None,
    expect: bool = True,
    verbose: bool = False,
    live: bool = False,
    timeout: 'Timeout' = None,
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
        verbose(bool): log executed command and location
        live(bool): if True log to stdout and stderr
        timeout(Timeout): limit maximum runtime, may use float instead/
    Returns:
        Completed process.
    Raises:
        TimeoutExpired: if timeout is defined and gracefully flag is not set

    >>> str(run('ls', verbose=True).returncode)
    cd...runtime(ls):...'0'
    """
    cwd = cwd if cwd else utila.cwdget()
    utila.exists_assert(cwd)
    msg = f'cwd {cwd} is not a valid directory'
    assert os.path.isdir(cwd), msg
    env = os.environ if env is None else env
    if verbose:
        utila.log(f'cd {cwd}')
        utila.log(cmd)
    timeout, gracefully, ontimeout = determine_timeout(timeout)
    with subprocess.Popen(  # nosec
            cmd,
            cwd=cwd,
            env=env,
            errors='replace',
            shell=True,
            stderr=None if live else subprocess.PIPE,
            stdout=None if live else subprocess.PIPE,
            universal_newlines=True,
    ) as proc:
        doit = utila.profile if verbose else utila.nothing
        with doit(msg=cmd, always=True):
            completed = handle_run(
                proc,
                expect,
                timeout,
                gracefully,
                ontimeout,
                cmd,
                cwd,
            )
    return completed


def exitx(msg='', returncode=utila.utils.FAILURE):
    """End progam. Log optional exit message as failure or success."""
    if msg:
        if returncode:
            utila.error(msg)
        else:
            utila.log(msg)
    sys.exit(returncode)


def handle_run(
    proc,
    expect,
    timeout,
    gracefully,
    ontimeout,
    cmd: str,
    cwd: str,
):
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        utila.error(f'timeout: {cmd} in {cwd} !failed!')
        proc.kill()
        if not gracefully:
            raise error
        if ontimeout:
            # run timeout callback
            ontimeout()
        return error
    completed = subprocess.CompletedProcess(
        args=cmd,
        returncode=proc.returncode,
        stderr=stderr,
        stdout=stdout,
    )
    if expect is True:
        assert_success(completed)
    if expect is False:  # pylint:disable=C2001
        assert_failure(completed)
    return completed


def determine_timeout(timeout):
    if timeout is None:
        return None, None, None
    if isinstance(timeout, (float, int)):
        return timeout, True, None
    return timeout.seconds, timeout.gracefully, timeout.ontimeout


def run_parallel(
    items: list,
    cwd: str = None,
    worker: int = 8,
    expect: bool = True,
    verbose: bool = False,
) -> int:
    """Run `items` as list of commands in parallel.

    Args:
        items: list of cmd's to run
        cwd: select current working directory
        worker: number of used threads
        expect: if True: fail on error
                if False: fail on success
                if None: return accumulated return code of executed processes
        verbose: inform about start and end of cmd execution
    Returns:
        Accumulated return code of executed processes.
    """
    ret = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        todo = {
            executor.submit(
                run,
                cmd=cmd,
                cwd=cwd,
                verbose=verbose,
            ): cmd for cmd in items
        }
        for future in concurrent.futures.as_completed(todo):
            current = todo[future]
            try:
                data = future.result()
                assert data.returncode == utila.SUCCESS, data
            except Exception as exc:  # pylint:disable=broad-except
                utila.error(f'{current} generated an exception: {exc}')
                ret += 1
    if expect:
        assert ret == utila.SUCCESS, str(ret)
    if expect is False:  # pylint:disable=C2001
        assert ret >= utila.FAILURE, str(ret)
    return ret


def fork(
    *runnables,
    worker: int = 6,
    process: bool = False,
    returncode: bool = False,
) -> int:
    """Run methods in parallel.

    Args:
        runnables(callable): callables to run
        worker(int): number of worker
        process(bool): if True use Process- instead of ThreadPool
        returncode(bool): always return `returncode` instead of computed
                          result
    Returns:
        returncode if error occurs or returncode=True
        result of computation if no error occurs or returncode is not used
    """
    failure = 0
    executor = concurrent.futures.ThreadPoolExecutor
    if process:
        executor = utila.select_executor()
    result = [None] * len(runnables)
    with executor(max_workers=worker) as pool:
        futures = {pool.submit(item): item for item in runnables}
        for future in concurrent.futures.as_completed(futures):
            index = runnables.index(futures[future])
            try:
                result[index] = future.result()
            except Exception as error:  # pylint:disable=broad-except
                utila.error(f'future number: {index}; {future} failed.')
                utila.error(error)
                utila.print_stacktrace()
                failure += 1
    if failure or returncode:
        return failure
    return result


class GeorgFork(contextlib.AbstractContextManager):
    """Fork methods to run in parallel."""

    def __init__(
        self,
        process: bool = True,
        returncode: bool = True,
        worker: int = None,
    ):
        self.process = process
        self.worker = worker
        self.returncode = returncode
        self.todo = []
        self.result = None

    def fork(self, method, **kwargs):
        runme = functools.partial(method, **kwargs)
        self.todo.append(runme)

    def __exit__(self, exc_type, exc_value, traceback):
        worker = len(self.todo) if self.worker is None else self.worker
        # run schedule
        self.result = utila.fork(
            *self.todo,
            process=self.process,
            returncode=self.returncode,
            worker=worker,
        )


def assert_success(process: subprocess.CompletedProcess):
    """Ensure that `process` completed correctly, if not a formatted
    information is logged"""
    assert process, str(process)
    assert process.returncode == utila.SUCCESS, utila.format_completed(process)


def assert_failure(process: subprocess.CompletedProcess):
    """Ensure that `process` fails. If process completed correctly, a
    formatted information is logged."""
    assert process, str(process)
    assert process.returncode != utila.SUCCESS, utila.format_completed(process)


def returnvalue(exception: Exception) -> int:
    """Determine return code raised from exit()"""
    msg = 'process return `None` as returnvalue instead of returncode'
    assert exception.value not in {None, 'None'}, msg
    try:
        return int(str(exception.value))
    except ValueError as error:
        utila.error(f'process does not provide exit value: {exception}')
        raise error


@dataclasses.dataclass
class Timeout:
    """\
    >>> Timeout(seconds=10) + 30
    40
    >>> 10 + Timeout(seconds=10)
    20
    """
    seconds: int = None
    gracefully: bool = True
    ontimeout: callable = None

    def __add__(self, value):
        # ease handling with numbers
        return self.seconds + value

    def __radd__(self, value):
        # ease handling with numbers
        return self.seconds + value


class Waiter:

    def __init__(self, lock=None, done=None):
        self.lock = threading.Lock() if not lock else lock
        self.done = {} if done is None else done

    def please(self, method, **kwargs):
        assert callable(method), str(method)
        inspected = str(inspect.signature(method))
        with self.lock:
            hashed = self.hashme(inspected)
            try:
                data = self.done[hashed]
            except KeyError:
                data = method(**kwargs)
                self.done[hashed] = data
        data = copy.deepcopy(data)
        return data

    def hashme(self, args):  # pylint:disable=R0201
        return hash(str(args))


def killpid(pid):
    """\
    COPIED FROM EXECNET
    """
    if hasattr(os, 'kill'):
        os.kill(pid, 15)
    elif utila.iswin():
        try:
            import ctypes
        except ImportError as ioerr:
            # T: treekill, F: Force
            cmd = f'taskkill /T /F /PID {pid}'.split()
            ret = subprocess.call(cmd)  # nosec
            if ret:
                raise EnvironmentError(f'taskkill returned: {ret!r}') from ioerr
        else:
            process_terminate = 1
            handle = ctypes.windll.kernel32.OpenProcess(
                process_terminate,
                False,
                pid,
            )
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
    else:
        raise EnvironmentError(f'no method to kill {pid}')


def process_ids(process: str) -> tuple:
    """Determine process ids of running application.

    #>>> assert process_ids('python')
    >>> process_ids('noprocess')
    ()
    """
    result = []
    cmd = f'ps | grep {process}'
    completed = utila.run(cmd, expect=None)
    raw = completed.stdout.strip()
    for line in raw.splitlines():
        if f'grep {process}' in line:
            # ps is linux displays themself when its runned, therefore the
            # process is always detected.
            continue
        index = int(line.split()[0])
        result.append(index)
    return tuple(result)
