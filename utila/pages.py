# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

from utila.utils import numbers


def pages(pattern: str, pagecount=None) -> tuple:
    """Determine list of pages out of given `pattern`.

    Args:
        pattern(str): user defined pattern
        pagecount(int): maximum number of pages for example `5:` -> 5:pagecount
                        not implement yet.
    Returns:
        list with user defined pages
    """

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
            if splitted[1] == '':
                # 50:
                splitted[1] = pagecount
            with contextlib.suppress(ValueError, TypeError):
                left = int(splitted[0])
                right = int(splitted[1])
                return list(range(left, right))
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
        parsed = parse_comma(pattern)
    elif ':' in pattern:
        parsed = parse_collon(pattern)
    else:
        parsed = parse_single(pattern)
    return tuple(parsed) if parsed else None


def should_skip(page: int, pages: tuple):  # pylint:disable=W0621
    """Determine if `page` is invalid

    If `pages` is None, every page is accepted.
    If `pages` is a list, only the elements in this list are valid and return
    False.

    Args:
        page(int): check to skip this page number
        pages(tuple): tuple with accepted pages, !require tuple to serialize!
    Returns:
        return True if `page` is in `pages` or pages is None else False
    """
    if pages is None:
        return False
    if not isinstance(pages, tuple):
        pages = (pages,)
    return not page in pages
