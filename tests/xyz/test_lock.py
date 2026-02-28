# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools

import utilotest

import utilo
import utilo.utils
import utilo.xyz.lock

lock = functools.partial(
    utilotest.run_cov,
    main=utilo.xyz.lock.main,
    process=utilo.xyz.lock.LOCK,
    expect=True,
)

unlock = functools.partial(
    utilotest.run_cov,
    main=utilo.xyz.lock.unlock,
    process=utilo.xyz.lock.UNLOCK,
    expect=True,
)


def test_lock_unlock(td, mp):
    example = td.tmpdir.join('exmaple.txt')
    utilo.file_create(
        example,
        'CONTENT',
    )
    assert not utilo.file_islocked(example)
    with mp.context() as context:
        context.setattr(utilo, 'wait', lambda: True)
        lock('', mp=mp)
    assert utilo.file_islocked(example)
    with mp.context() as context:
        context.setattr(utilo, 'wait', lambda: True)
        unlock('', mp=mp)
    assert not utilo.file_islocked(example)
