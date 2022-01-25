# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


@utila.empty_replace(member=10, glember='hello')
def replace_default(first=None, glember=utila.EMPTY, member=utila.EMPTY):
    return first, member, glember


def test_empty_replace():
    assert replace_default('?', None) == ('?', 10, None)


def test_empty_replace_invalid_signature_does_not_match():
    with pytest.raises(ValueError):

        @utila.empty_replace(tember=10, september='hello')
        def replacce(first=None, member=utila.EMPTY, glember=utila.EMPTY):
            return first, member, glember


def test_empty_replace_invalid_signature_missing_default():
    with pytest.raises(ValueError):

        @utila.empty_replace(member=1, glember=2, tember=3)
        def replacce(first=None, member=utila.EMPTY, glember=utila.EMPTY):
            return first, member, glember
