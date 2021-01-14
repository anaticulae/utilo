# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utilatest

import utila


def test_process_run_parallel():
    items = []
    for _ in range(12):
        items.append('ls')

    success = utila.run_parallel(items)
    assert success == utila.SUCCESS

    failures = ['wasd']
    error = utila.run_parallel(failures, expect=False)
    assert error >= utila.FAILURE


def test_fork():

    def first():
        pass

    def second():
        assert 0

    completed = utila.fork(first, second, worker=3)
    assert completed != utila.SUCCESS


def test_georg_fork(capsys):

    def first(a, b):  # pylint:disable=C0103
        utila.log(f'{a} {b}')

    def second(c, d=13):  # pylint:disable=C0103
        utila.log(f'{c} {d}')

    with utila.GeorgFork() as todo:
        todo.fork(first, a=10, b=10)
        todo.fork(second, c=5)

    stdout = utilatest.stdout(capsys)
    assert '10 10' in stdout
    assert '5 13' in stdout
