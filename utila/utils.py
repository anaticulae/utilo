#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import sys

SUCCESS = 0
FAILURE = 1

TMP = '.tmp'
UTF8 = 'utf8'
NEWLINE = '\n'
INF = (1 << 31) - 1

NDIGITS = 2

ALL_PAGES = ':'


def forward_slash(content: str):
    """Replace every backward slash \\ with an forward slash /

    Args:
        content(str): content with backslashs
    Returns:
        content without backslashs
    """
    content = str(content).replace(r'\\', '/').replace('\\', '/')
    return content


def fix_encoding(msg: str):
    """Remove invalid character to display on console

    Args:
        msg(str): message with invalid character
    Returns:
        message `without` invalid character"""

    # ensure to have str
    msg = str(msg)

    # Convert for windows console, replace non supported chars
    encoding = 'cp1252' if sys.platform in ('win32', 'cygwin') else 'utf-8'

    # remove non valid char to avoid error on (win)-console
    msg = msg.encode(encoding, errors='xmlcharrefreplace').decode(encoding)
    return msg


def roundme(value: float):
    """Round value to `NDGITS`=2"""
    return round(value, NDIGITS)


def flatten(lists):
    """Chain lists of list to one list"""
    result = []
    for item in lists:
        result.extend(item)
    return result


def determine_order(requirements, flat=True):
    requirements = dict(requirements)
    todo = list(requirements.keys())
    result = []
    while todo:
        level = []
        before = len(todo)
        for item in todo[:]:
            if any([current in todo for current in requirements[item]]):
                continue
            todo.remove(item)
            level.append(item)
        result.append(level)
        assert len(todo) != before, 'zyclic definition of workplan'
    if flat:
        result = flatten(result)
    return result


def pages(pattern: str, pagecount=None) -> list:
    """Determine list of pages out of given `pattern`.

    Args:
        pattern(str): user defined pattern
        pagecount(int): maximum number of pages for example `5:` -> 5:pagecount
                        not implement yet.
    Returns:
        list with user defined pages
    """

    # TODO: implement pagecount

    def parse_comma(pattern):
        """Pattern contains `,`"""
        splitted = numbers(pattern.split(','))
        if not all([isinstance(item, int) for item in splitted]):
            return None
        return splitted

    def parse_collon(pattern):
        """Pattern contains `:`"""
        if len(pattern) == 1:
            # single :
            return []
        splitted = pattern.split(':')
        if len(splitted) == 1:
            return [int(splitted[0])]
        if len(splitted) == 2:
            # left, right
            try:
                left = int(splitted[0])
                right = int(splitted[1])
                return list(range(left, right))
            except ValueError:
                return None
        return None

    def parse_single(pattern):
        """Pattern contains no special character"""
        try:
            return [int(pattern)]
        except ValueError:
            return None

    pattern = pattern.strip()
    if not pattern:
        return None
    if ',' in pattern:
        return parse_comma(pattern)
    if ':' in pattern:
        return parse_collon(pattern)
    return parse_single(pattern)


def numbers(items):
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            result.append(None)
    return result
