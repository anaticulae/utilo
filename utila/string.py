# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
import sys

import utila.math


def forward_slash(content: str, save_newline: bool = True) -> str:
    """Replace every backward slash \\ with an forward slash /.

    Args:
        content(str): content with backslashs
        save_newline(bool): if True, do not convert \n to /n
    Returns:
        content without backslashs
    """
    # TODO: LEARN MORE ABOUT REGEX
    safety_token = '_1337THISISSECRET1337_'
    if save_newline:
        content = content.replace(r'\n', safety_token)

    content = content.replace(r'\\', '/').replace('\\', '/')

    if save_newline:
        content = content.replace(safety_token, r'\n')
    return content


def fix_encoding(msg: str) -> str:
    """Remove invalid character to display on console

    Args:
        msg(str): message with invalid character
    Returns:
        message `without` invalid character
    """
    # ensure to have str
    msg = str(msg)

    # Convert for windows console, replace non supported chars
    encoding = 'cp1252' if sys.platform in ('win32', 'cygwin') else 'utf-8'

    # remove non valid char to avoid error on (win)-console
    msg = msg.encode(encoding, errors='xmlcharrefreplace').decode(encoding)
    return msg


def extract_match(matched: re.Match) -> str:
    """Extract content out of `re.Match`."""
    assert isinstance(matched, re.Match), type(matched)
    return matched.string[matched.span()[0]:matched.span()[1]]


def parse_tuple(raw: str, expected_length: int = 4) -> tuple:
    """Convert `raw` to tuple of floats."""
    items = (float(item) for item in raw.split())
    items = utila.math.roundme(*items)
    items = tuple(items)
    assert len(items) == expected_length, f'could not parse {raw}'
    return items
