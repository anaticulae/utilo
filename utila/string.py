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
import utila.utils


def forward_slash(content: str, save_newline: bool = True) -> str:
    r"""Replace every backward slash \\ with an forward slash /.

    Args:
        content(str): content with backslashs
        save_newline(bool): if True, do not convert \n to /n
    Returns:
        content without backslashs

    Examples:
    >>> forward_slash('\\helm\nelm')
    '/helm\nelm'
    >>> forward_slash('\\helm\\telm')
    '/helm/telm'
    >>> forward_slash('\\helm\\nelm', save_newline=False)
    '/helm/nelm'
    """
    pattern = r'\\'
    if save_newline:
        pattern = r'\\(?!n)'
    content = re.sub(re.compile(pattern), '/', content)
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
    # convert for windows console
    encoding = 'cp1252' if sys.platform in ('win32', 'cygwin') else 'utf-8'
    # remove non valid char to avoid errors on win-console
    msg = msg.encode(encoding, errors='xmlcharrefreplace').decode(encoding)
    return msg


def extract_match(matched: re.Match) -> str:
    """Extract content out of `re.Match`."""
    assert isinstance(matched, re.Match), type(matched)
    return matched.string[matched.span()[0]:matched.span()[1]]


def parse_tuple(raw: str, length: int = 4, typ=float) -> tuple:
    """Convert `raw` to tuple of `typ`.

    >>> parse_tuple('True false True False true', length=5, typ=bool)
    (True, False, True, False, True)
    """
    if typ is int:
        typ = utila.str2int
    if typ is bool:
        typ = utila.str2bool
    items = (typ(item) for item in raw.split())
    if typ is float:
        items = utila.math.roundme(*items)
    items = tuple(items)
    assert len(items) == length, f'could not parse {raw}'
    return items


def normalize_whitespaces(text: str) -> str:
    """Remove unnecessary white spaces.

    >>> normalize_whitespaces(' make    me happy' + utila.NEWLINE)
    'make me happy'
    """
    return ' '.join(text.strip().split())
