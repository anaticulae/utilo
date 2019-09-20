# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
import sys

import pytest

import utila


@pytest.mark.parametrize('platform,given,expected', [
    ('win32', '\x80', '&#128;'),
    ('cygwin', '\x80', '&#128;'),
    ('linux', '\x80', '\x80'),
])
def test_fix_encoding(platform, given, expected, monkeypatch):
    """Fix encoding depending used platform"""
    with monkeypatch.context() as context:
        context.setattr(sys, 'platform', platform)
        fixed = utila.fix_encoding(given)
    assert fixed == expected


def test_string_forward_slash_do_not_replace_newline():
    text_with_newline = r'Hello\n\nHello' + '\n'
    forwarded = utila.forward_slash(text_with_newline)
    assert forwarded == text_with_newline


@pytest.mark.parametrize('string, expected', [
    pytest.param(r'\wello\dister', r'/wello/dister', id='replace backslash'),
    pytest.param(r'\n', r'\n', id='do not replace raw newline'),
    pytest.param('\n', '\n', id='do not replace newline'),
    pytest.param('\\\n', '/\n', id='replace backslash before newline'),
])
def test_string_forward_slash_replace_backslash(string, expected):
    replaced = utila.forward_slash(string)
    assert replaced == expected
