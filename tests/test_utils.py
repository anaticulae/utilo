# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

from pytest import mark

from utila import fix_encoding


@mark.parametrize('platform,given,expected', [
    ('win32', '\x80', '&#128;'),
    ('cygwin', '\x80', '&#128;'),
    ('linux', '\x80', '\x80'),
])
def test_fix_encoding(platform, given, expected, monkeypatch):
    """Fix encoding depending used platform"""
    with monkeypatch.context() as context:
        context.setattr(sys, 'platform', platform)
        fixed = fix_encoding(given)
    assert fixed == expected
