# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


def test_file_utils_verify_decorator():

    @utila.pathexists
    def mojo_file(inpath: int, path: str, config: float):  # pylint:disable=W0613
        return 10

    assert mojo_file(12, __file__, config=1.3) == 10

    with pytest.raises(AssertionError):
        mojo_file(20, 'file_does_not_exists.txt', 30)


def test_file_utils_verify_invalid_decorator():

    @utila.pathexists
    def nopath(abc):
        return abc

    with pytest.raises(TypeError):
        nopath(10)
