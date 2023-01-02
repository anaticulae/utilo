# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def work() -> list[tuple[str, bytes]]:
    result = [
        ('info: yaml', (b'content', 'bin')),
        ('second: yaml', (b'second content', 'bib')),
        ('third yaml', (b'third content', 'png')),
    ]
    return result
