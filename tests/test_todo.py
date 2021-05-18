# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


def test_refactor_contextmanager(monkeypatch):
    with utila.refactor(major=5, minor=10):
        pass

    with pytest.raises(AssertionError):
        with utila.refactor(major=1, minor=1):
            pass

    with monkeypatch.context() as context:
        context.setattr(utila, '__version__', '2.1.0')
        with pytest.raises(AssertionError):
            with utila.refactor(major=2, minor=1, patch=0):
                pass


def test_refactor_decorator():

    @utila.refactor(major=5, minor=1)  # pylint:disable=W0612
    class ValidVersion:  # pylint:disable=W0612
        pass

    with pytest.raises(AssertionError):

        @utila.refactor(major=1, minor=1)  # pylint:disable=W0612,W0621
        class OutdatedVersion:  # pylint:disable=W0612
            pass

    @utila.refactor(major=5, minor=1)
    def ten():
        # ensure that decorator does not overwrite return result
        return 10

    assert ten() == 10
