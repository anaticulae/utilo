# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re

NOCASE_VERBOSE = re.I | re.X


def extract_match(matched) -> str:
    """Extract content out of `re.Match`."""
    assert isinstance(matched, re.Match), type(matched)
    return matched.string[matched.span()[0]:matched.span()[1]]


def match(pattern: str, content: str, flags=None):
    r"""\
    >>> match(r'Abc\:', 'abc:')
    <re.Match object; span=(0, 4), match='abc:'>
    """
    return re.match(pattern, content.strip(), flags=flags or NOCASE_VERBOSE)


def search(pattern: str, content: str, flags=None):
    r"""\
    >>> search(r'Abc\:', 'abc: ende')
    <re.Match object; span=(0, 4), match='abc:'>
    """
    if not isinstance(pattern, str):
        return pattern.search(content.strip())
    return re.search(pattern, content.strip(), flags=flags or NOCASE_VERBOSE)


def compiles(pattern: str, flags=None):
    r"""\
    >>> compiles(r'\d+10 HELLO')
    re.compile('\\d+10 HELLO', re.IGNORECASE|re.VERBOSE)
    """
    return re.compile(pattern, flags=flags or NOCASE_VERBOSE)


def finditer(pattern: str, text: str, flags=None):
    r"""\
    >>> [extract_match(item) for item in finditer(pattern=r'\d+', text=r'   10 HELLO 38 19')]
    ['10', '38', '19']
    >>> len(list(finditer(pattern=compiles(r'\d+'), text=r'   10 HELLO 38 19')))
    3
    """
    if not isinstance(pattern, str):
        return pattern.finditer(text)
    result = re.finditer(pattern, text, flags=flags or NOCASE_VERBOSE)
    return result
