# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utilo


def test_refactor_contextmanager(mp):
    with utilo.refactor(major=5, minor=10):
        pass

    with pytest.raises(AssertionError):
        with utilo.refactor(major=1, minor=1):
            pass

    with mp.context() as context:
        context.setattr(utilo, '__version__', '2.1.0')
        with pytest.raises(AssertionError):
            with utilo.refactor(major=2, minor=1, patch=0):
                pass


def test_refactor_decorator():

    @utilo.refactor(major=5, minor=1)  # pylint:disable=W0612
    class ValidVersion:  # pylint:disable=W0612
        pass

    with pytest.raises(AssertionError):

        @utilo.refactor(major=1, minor=1)  # pylint:disable=W0612,W0621
        class OutdatedVersion:  # pylint:disable=W0612
            pass

    @utilo.refactor(major=5, minor=1)
    def ten():
        # ensure that decorator does not overwrite return result
        return 10

    assert ten() == 10
