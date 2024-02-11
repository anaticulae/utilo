# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import utilatest

import utila
import utila.utils
import utila.xyz.lock

lock = functools.partial(
    utilatest.run_cov,
    main=utila.xyz.lock.main,
    process=utila.xyz.lock.LOCK,
    expect=True,
)

unlock = functools.partial(
    utilatest.run_cov,
    main=utila.xyz.lock.unlock,
    process=utila.xyz.lock.UNLOCK,
    expect=True,
)


def test_lock_unlock(td, mp):
    example = td.tmpdir.join('exmaple.txt')
    utila.file_create(
        example,
        'CONTENT',
    )
    assert not utila.file_islocked(example)
    with mp.context() as context:
        context.setattr(utila, 'wait', lambda: True)
        lock('', mp=mp)
    assert utila.file_islocked(example)
    with mp.context() as context:
        context.setattr(utila, 'wait', lambda: True)
        unlock('', mp=mp)
    assert not utila.file_islocked(example)
