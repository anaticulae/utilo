# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import typing

import utila.math


def parse_pages(pattern: str, pagecount=None) -> tuple:  # pylint:disable=too-complex
    """Determine unique, sorted tuple of pages out of given `pattern`.

    Args:
        pattern(str): user defined pattern
        pagecount(int): maximum number of pages - for example
                        `5:` -> 5:pagecount
    Returns:
        tuple of user defined pages

    Examples:
    >>> parse_pages('2:5')
    (2, 3, 4)
    >>> parse_pages('0:', pagecount=5)
    (0, 1, 2, 3, 4)
    >>> parse_pages('1, 1, 2, 3, 3')
    (1, 2, 3)
    >>> parse_pages('10:13, 3')
    (3, 10, 11, 12)
    >>> parse_pages('10:13, 3:5')
    (3, 4, 10, 11, 12)
    >>> parse_pages(':5')
    (0, 1, 2, 3, 4)
    """

    def parse_comma(pattern):
        """Pattern contains `,`"""
        splitted = pattern.split(',')
        result = [parse_pages(item, pagecount) for item in splitted]
        if [item for item in result if item is None]:
            return None
        result = utila.flatten(result)
        return result

    def parse_collon(pattern):
        """Pattern contains `:`"""
        if len(pattern) == 1:
            # single :
            return []
        splitted = pattern.split(':')
        # Example 50:
        splitted[1] = pagecount if splitted[1] == '' else splitted[1]
        # Example :5
        splitted[0] = 0 if splitted[0] == '' else splitted[0]
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
    if not parsed:
        return None
    parsed = utila.make_unique(parsed)
    parsed = sorted(parsed)
    return tuple(parsed)


PageNumbers = typing.TypeVar('PageNumbers', int, tuple)


def should_skip(page: PageNumbers, pages: tuple) -> bool:  # pylint:disable=W0621
    """Determine if `page` is invalid.

    If `pages` is None, every page is accepted.
    If `pages` is a tuple, only the elements in tuple are valid and
    return False.

    Args:
        page(int): check to skip this page number
        pages(tuple): tuple with accepted pages, !require tuple to serialize!
    Returns:
        return True if `page` is in `pages` or pages is None else False

    Examples:
    >>> should_skip(5, (1, 2, 3))
    True
    >>> should_skip(5, None)
    False
    >>> should_skip(6, 5)
    True
    >>> should_skip((4, 5, 6), [1, 2, 3, 4, 5])
    True
    """
    if pages is None:
        return False
    if not isinstance(pages, tuple):
        pages = (pages,)
    # support multiple pages
    if isinstance(page, tuple):
        # ensure that all (page..) are in range, all selected and all inside
        start, end = min(page), max(page)
        return any([should_skip(pp, pages) for pp in range(start, end + 1)])
    return not page in pages


PageContent = typing.TypeVar('PageContent', typing.List, typing.Dict)


def select_page(
        items: PageContent,
        page: int,
        default: typing.Any = None,
) -> typing.Any:
    """Select item depending on `page`-attribute of the item.

    Args:
        items(collection): content which contains the pages
        page(int): page-attribute to select from `items`
        default: returned if `page` does not exists
    Returns:
        page with page-attribute matches with `page`
    Raises:
        ValueError: if items contains duplicated page number
        ValueError: if no items are passed

    Examples:
    >>> select_page(items={0 : 'first', 1 : 'second'}, page=1)
    'second'
    """
    if items is None:
        raise ValueError('no items provided')
    if not isinstance(items, dict):
        pages = sorted([item.page for item in items])
        items = {item.page: item for item in items}
        if len(items) != len(pages):
            raise ValueError(f'duplicated page attributes: {pages}')
    try:
        return items[page]
    except KeyError:
        return default
