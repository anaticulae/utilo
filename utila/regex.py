# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re

NOCASE_VERBOSE = re.I | re.X


def extract_match(matched) -> str:
    """Extract content out of `re.Match`."""
    assert isinstance(matched, re.Match), type(matched)
    return matched.string[matched.span()[0]:matched.span()[1]]


def match(pattern: str, content: str):
    r"""\
    >>> match(r'Abc\:', 'abc:')
    <re.Match object; span=(0, 4), match='abc:'>
    """
    return re.match(pattern, content.strip(), flags=NOCASE_VERBOSE)


def search(pattern: str, content: str):
    return re.search(pattern, content.strip(), flags=NOCASE_VERBOSE)


def compiles(pattern: str):
    r"""\
    >>> compiles(r'\d+10 HELLO')
    re.compile('\\d+10 HELLO', re.IGNORECASE|re.VERBOSE)
    """
    return re.compile(pattern, flags=NOCASE_VERBOSE)
