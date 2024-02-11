# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila

EXPECTED = """\
=========================
||(0x0)     |          ||
=========================
||          |(1x1)     ||
||          |(1x1)     ||
||          |(1x1)     ||
||          |(1x1)     ||
=========================
||          |(1x2)     ||
=========================
"""


def test_table_print():
    table = utila.TablePrinter(2, 3, width=10, height=10)
    table.insert(0, 0, '(0x0)')
    table.insert(1, 1, '(1x1)')
    table.insert(1, 1, '(1x1)')
    table.insert(1, 1, '(1x1)')
    table.insert(1, 1, '(1x1)')
    table.insert(1, 2, '(1x2)')
    raw = str(table)
    assert raw == EXPECTED


SMALLEST = """\

1     3     2
2     4     2
3     5
hello wello dell
"""


def test_table_smallest():
    table = [
        (
            (1, 2, 3),
            (3, 4, 5),
            (2, 2),
        ),
        ('hello', 'wello', 'dell'),
    ]
    raw = utila.table_smallest(table)
    assert raw == SMALLEST
