# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent
import concurrent.futures
import contextlib
import functools
import os
import subprocess  # nosec

import utila


def run(
        cmd: str,
        cwd: str = None,
        env: dict = None,
        expect: bool = True,
        verbose: bool = False,
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
    Returns:
        Completed process.
    """
    cwd = cwd if cwd else os.getcwd()
    assert os.path.exists(cwd)
    msg = f'cwd {cwd} is not a valid directory'
    assert os.path.isdir(cwd), msg

    env = os.environ if env is None else env

    if verbose:
        utila.log(f'cd {cwd}')
        utila.log(cmd)

    completed = subprocess.run(  #nosec
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


def run_parallel(
        items: list,
        cwd: str = None,
        worker: int = 8,
        expect: bool = True,
) -> int:
    """Run `items` as list of commands in parallel.

    Args:
        items: list of cmds to run
        cwd: select current working directory
        worker: number of used threads
        expect: if True: fail on error, if False: fail on success, if None:
                return accumulated return code of executed processes.
    Returns:
        Accumulated return code of executed processes.
    """
    ret = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        todo = {executor.submit(run, cmd, cwd): cmd for cmd in items}
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
    if expect is False:
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
    """Ensure that `process` completed correctly, if not a formated
    information is logged"""
    assert process, str(process)
    assert process.returncode == utila.SUCCESS, utila.format_completed(process)


def assert_failure(process: subprocess.CompletedProcess):
    """Ensure that `process` fails. If process completed correctly, a
    formated information is logged."""
    assert process, str(process)
    assert process.returncode != utila.SUCCESS, utila.format_completed(process)


def returnvalue(exeception: Exception) -> int:
    """Determine return code raised from exit()"""
    msg = 'process return `None` as returnvalue instead of returncode'
    assert exeception.value not in (None, 'None'), msg
    return int(str(exeception.value))
