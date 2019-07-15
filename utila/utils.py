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
