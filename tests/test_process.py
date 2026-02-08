# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import subprocess  # nosec
import time

import pytest
import utilatest

import utilo


def test_process_run_parallel():
    items = []
    for _ in range(12):
        items.append('ls')

    success = utilo.run_parallel(items)
    assert success == utilo.SUCCESS

    failures = ['wasd']
    error = utilo.run_parallel(failures, expect=False)
    assert error >= utilo.FAILURE


def test_fork():

    def first():
        pass

    def second():
        assert 0

    completed = utilo.fork(first, second, worker=3)
    assert completed != utilo.SUCCESS


def test_georg_fork(capsys):

    def first(a, b):  # pylint:disable=C0103
        utilo.log(f'{a} {b}')

    def second(c, d=13):  # pylint:disable=C0103
        utilo.log(f'{c} {d}')

    with utilo.GeorgFork() as todo:
        todo.fork(first, a=10, b=10)
        todo.fork(second, c=5)

    stdout = utilatest.stdout(capsys)
    assert '10 10' in stdout
    assert '5 13' in stdout


def test_run_timeout_complex():
    cmd = 'sleep 2'
    error = utilo.run(cmd, timeout=utilo.Timeout(seconds=0))
    assert isinstance(error, subprocess.TimeoutExpired)


def test_run_timeout_float():
    cmd = 'sleep 2'
    error = utilo.run(cmd, timeout=0.0)
    assert isinstance(error, subprocess.TimeoutExpired)


def test_run_timeout_not_gracefully():
    cmd = 'sleep 2'
    with pytest.raises(subprocess.TimeoutExpired):
        utilo.run(cmd, timeout=utilo.Timeout(seconds=0, gracefully=False))


@pytest.mark.timeout(4, method="thread")
def test_waiter():
    """Use `timeout` to verify that caching works."""

    def run(a: int, b: int):  # pylint:disable=C0103
        time.sleep(1)
        return a + b

    waiter = utilo.Waiter()
    first = waiter.please(run, a=10, b=10)
    waiter.please(run, a=15, b=10)
    third = waiter.please(run, a=10, b=10)
    assert first == third
    for _ in range(10):
        assert waiter.please(run, a=15, b=10)


def test_exit():
    with pytest.raises(SystemExit):
        utilo.exitx('this is a failure')
