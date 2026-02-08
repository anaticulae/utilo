# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
>>> DATA = 'A B C D E F G H I'.split()
>>> MIXED = DATA[1:3] + [DATA[4], DATA[3]] + [DATA[0]] + DATA[5:]
>>> print(diffview(DATA, MIXED))
<b>A</b>
B
C
<b>D</b>
E
<del>D</del>
<del>A</del>
F
G
H
"""

import difflib

import utilo


def diffview(expected: list, current: list, html: bool = True) -> str:
    expected = [f' {item}' for item in expected]
    current = [f' {item}' for item in current]
    diffed = difflib.unified_diff(current, expected, lineterm='')
    # remove header
    raw = list(diffed)[3:]
    if html:
        raw = [
            f'<del>{item[1:].strip()}</del>' if item[0] == '-' else item
            for item in raw
        ]
        raw = [
            f'<b>{item[1:].strip()}</b>' if item[0] == '+' else item
            for item in raw
        ]
    result = utilo.strip(*raw)
    result = utilo.NEWLINE.join(result)
    return result
