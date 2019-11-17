# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import typing

from utila.utils import numbers


def parse_pages(pattern: str, pagecount=None) -> tuple:  # pylint:disable=too-complex
    """Determine list of pages out of given `pattern`.

    Args:
        pattern(str): user defined pattern
        pagecount(int): maximum number of pages for example `5:` -> 5:pagecount
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


PageNumbers = typing.TypeVar('PageNumbers', int, tuple)


def should_skip(page: PageNumbers, pages: tuple) -> bool:  # pylint:disable=W0621
    """Determine if `page` is invalid.

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
    # support multiple pages
    if isinstance(page, tuple):
        # ensure that all (page..) are in range
        start, end = page
        return any([should_skip(pp, pages) for pp in range(start, end + 1)])
    return not page in pages


def select_page(items, page: int, default=None):
    """Select item depending on `page`-attribute of the item.

    Args:
        items(collection): content which contains the pages
        page(int): page-attribute to select from `items`
        default: returned if `pagenumber` does not exists
    Returns:
        page with page-attribute matches with `page`
    Raises:
        ValueError: if items contains duplicated page number
        ValueError: if no items are passed
    """
    if items is None:
        raise ValueError('no items provided')
    if not isinstance(items, dict):
        before = len(items)
        items = {item.page: item for item in items}
        if len(items) != before:
            raise ValueError('duplicated page attribute')
    try:
        return items[page]
    except KeyError:
        return default
