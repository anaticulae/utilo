# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

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
