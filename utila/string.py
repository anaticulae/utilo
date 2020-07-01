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


def forward_slash(content: str, newline: bool = False) -> str:
    r"""Replace every backward slash \\ with an forward slash /.

    Args:
        content(str): content with backslashs
        newline(bool): if True, do not convert \n to /n
    Returns:
        content without backslashs

    Examples:
    >>> forward_slash('\\helm\nelm', newline=True)
    '/helm\nelm'
    >>> forward_slash('\\helm\\telm', newline=True)
    '/helm/telm'
    >>> forward_slash('\\helm\\nelm')
    '/helm/nelm'
    """
    pattern = r'\\'
    if newline:
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


def normalize_whitespaces(text: str) -> str:
    r"""Remove unnecessary white spaces.

    >>> normalize_whitespaces(' make    me happy' + '\n')
    'make me happy'
    """
    return ' '.join(text.strip().split())


def istemplate_replaced(text: str):
    """Check if some pattern `{% %}` is not replaced.

    >>> istemplate_replaced('hello')
    True
    >>> istemplate_replaced('%}')
    False
    """
    if '{%' in text:
        return False
    if '%}' in text:
        return False
    return True


def shrink(content: str, maxlength: int = 300) -> str:
    """\
    >>> shrink('abcdefg', maxlength=6)
    'abc[...]efg'
    >>> shrink(b'bytesbytesbytes', maxlength=10)
    'bytes[...]bytes'
    >>> shrink('abcdefg')
    'abcdefg'

    without converting list to str, this example would produce a longt
    string, cause max length will check against list length:
    >>> shrink(['a'*1000]*5, 6)
    "['a[...]a']"
    """
    assert maxlength >= 0, str(maxlength)
    if isinstance(content, bytes):
        content = content.decode('utf8', errors='replace')
    else:
        # convert list, int etc. to str
        content = str(content)
    if len(content) <= maxlength:
        return content
    half = int(maxlength / 2)
    before = content[0:half]
    after = content[-half:]
    result = f'{before}[...]{after}'
    return result
