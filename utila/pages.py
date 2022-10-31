# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import contextlib
import math
import typing

import utila


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
    >>> parse_pages('-5:', pagecount=50)
    (45, 46, 47, 48, 49)

    Python range syntax, -1 means 10-1:10; more simple 9:10; 9
    >>> parse_pages('-1', pagecount=10)
    (9,)

    How to handle negative page numbers? Use `_` to signal that a page
    number is negative to avoid struggle with python range syntax -3:10,
    eg 7:10.

    >>> parse_pages('_5:2')
    (-5, -4, -3, -2, -1, 0, 1)
    >>> parse_pages('_5:_2')
    (-5, -4, -3)
    """
    pattern = pattern.strip()
    if not pattern:
        return None
    if ',' in pattern:
        parsed = parse_comma(pattern, pagecount)
    elif ':' in pattern:
        parsed = parse_collon(pattern, pagecount)
    else:
        parsed = parse_single(pattern, pagecount)
    if not parsed:
        return None
    # make unique and sorted
    parsed = sorted(set(parsed))
    return tuple(parsed)


def pages_inside(pages: tuple, minn: int = 0, maxx=None) -> tuple:
    """\
    >>> pages_inside(None, 5, 10)
    (5, 6, 7, 8, 9, 10)
    >>> pages_inside((0, 1, 2, 3, 4, 5), 2, maxx=4)
    (2, 3, 4)
    """
    if not pages:
        if maxx is None:
            return None
        return utila.rtuple(minn, maxx + 1)
    pages = tuple(item for item in pages if minn <= item <= maxx)
    return pages


def parse_comma(pattern, pagecount):
    """Pattern contains `,`"""
    splitted = pattern.split(',')
    result = [parse_pages(item, pagecount) for item in splitted]
    if [item for item in result if item is None]:
        return None
    result = utila.flat(result)
    return result


def parse_collon(pattern, pagecount=None):
    """Pattern contains `:`

    >>> parse_collon('_5:2')
    [-5, -4, -3, -2, -1, 0, 1]
    """
    if len(pattern) == 1:
        # single :
        return []
    splitted = pattern.split(':')
    # Example 50:
    splitted[1] = pagecount if splitted[1] == '' else splitted[1]  # pylint:disable=C1901
    # Example :5
    splitted[0] = '0' if splitted[0] == '' else splitted[0]  # pylint:disable=C1901
    with contextlib.suppress(ValueError, TypeError):
        left = parse_special_pagenumber(splitted[0])
        right = parse_special_pagenumber(splitted[1])
        specialpattern = '_' in splitted[0]
        if left < 0 and not specialpattern:
            # -5:
            left = right + left
        return list(range(left, right))
    return None


def parse_special_pagenumber(item: str) -> int:
    """\
    >>> parse_special_pagenumber('_5')
    -5
    """
    item = str(item).replace('_', '-')
    return int(item)


def parse_single(pattern, pagecount):
    """Pattern contains no special character"""
    try:
        single = int(pattern)
        if single < 0:
            return [pagecount + single]
        return [single]
    except ValueError:
        return None


PageNumbers = typing.TypeVar('PageNumbers', int, tuple)
Iterable = (list, tuple)


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
    >>> should_skip(2, [1, 2, 3])
    False
    >>> should_skip(5, None)
    False
    >>> should_skip(6, 5)
    True
    >>> should_skip((4, 5, 6), [1, 2, 3, 4, 5])
    True
    >>> should_skip((0.0, 0.5), (0, 1, 2, 3))
    False
    >>> should_skip((0.0, 0.5), (0,))
    True
    >>> should_skip((0.0, 0.5), (0, 1))
    False
    """
    if pages is None:
        return False
    if not isinstance(pages, Iterable):
        pages = (pages,)
    # support multiple pages
    if isinstance(page, Iterable):
        # ensure that all (page..) are in range, all selected and all inside
        start, end = min(page), max(page)
        start, end = math.floor(start), math.ceil(end)
        return any(should_skip(pp, pages) for pp in range(start, end + 1))
    return page not in pages


class SelectPage:
    """\
    >>> pages = SelectPage(items={0 : 'first', 1 : 'second'}, default=10)
    >>> pages.getpage(1)
    'second'
    >>> pages.getpage(2)
    10
    >>> pages.getpage(0)
    'first'
    >>> pages.getpages((0, 1, 2, 3, 4, 5))
    ['first', 'second', 10, 10, 10, 10]
    >>> double = SelectPage(default=None, first={2 : 'first', 4 : 'second'},
    ... single={0 : '1', 1 : '2'})
    >>> double.getpages((0, 1, 2, 3, 4, 5))
    [(None, '1'), (None, '2'), ('first', None), None, ('second', None), None]
    """

    def __init__(self, default=None, **kwargs):
        self.default = default
        self.count = len(kwargs)
        self.data = self.prepare_data(kwargs)

    def prepare_data(self, kwargs) -> dict:
        data = collections.defaultdict(list)
        for index, kwdata in enumerate(kwargs.values()):
            if not isinstance(kwdata, dict):
                kwdata = self.convert_nodict(kwdata)
            for page, value in kwdata.items():
                if len(data[page]) == index:
                    data[page].append(value)
                    continue
                for _ in range(index):
                    data[page].append(None)
                data[page].append(value)
        for item in data.values():
            while len(item) < self.count:  # pylint:disable=W0149
                item.append(None)
        result = dict(data)
        return result

    def convert_nodict(self, items):  # pylint:disable=R0201
        if any(item is None for item in items):
            raise ValueError(f'`items` contain `None` pages: {items}')
        pages = sorted([item.page for item in items])
        items: dict = {item.page: item for item in items}
        if len(items) != len(pages):
            raise ValueError(f'duplicated page attributes: {pages}')
        return items

    @utila.cacheme
    def getpage(self, page: int) -> tuple:
        try:
            data = self.data[page]
        except KeyError:
            return self.default
        if self.count == 1:
            return data[0]
        return tuple(data)

    @utila.cacheme
    def getpages(self, pages: tuple) -> list:
        assert len(pages) == len(set(pages)), f'duplicated pages: {pages}'
        pages = sorted(pages)
        result = [self.getpage(page) for page in pages]
        return result


PageContent = typing.TypeVar('PageContent', list, dict)


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

    >>> import collections
    >>> PageItem = collections.namedtuple('PageItem', 'page, content')

    >>> select_page(items=[None, PageItem(1, 'content')], page=1)
    Traceback (most recent call last):
        ...
    ValueError: `items` contain `None` pages: ...
    """
    assert isinstance(page, int), type(page)
    if items is None:
        raise ValueError('no items provided')
    if not isinstance(items, dict):
        if any(item is None for item in items):
            raise ValueError(f'`items` contain `None` pages: {items}')
        pages = sorted([item.page for item in items])
        items = {item.page: item for item in items}
        if len(items) != len(pages):
            raise ValueError(f'duplicated page attributes: {pages}')
    try:
        return items[page]
    except KeyError:
        return default


def select_pages(
    items: PageContent,
    pages: tuple,
    default: typing.Any = None,
) -> typing.Any:
    """Select items depending on `page`-attribute of the item.

    See: `select_page`"""
    assert len(pages) == len(set(pages)), f'duplicated pages: {pages}'
    pages = sorted(pages)
    result = []
    for page in pages:
        result.append(select_page(items, page=page, default=default))
    return result


def select_content(
    items: PageContent,
    page: int,
    default: typing.Any = None,
) -> typing.Any:
    selected = select_page(items, page=page)
    if selected:
        return selected.content
    return default


def some(items) -> bool:
    """Return True if any item is not None.

    >>> some((None, None, None))
    False
    >>> some(([], None, None))
    True
    """
    return any(item is not None for item in items)


def sync_pages(
    iterators,
    *,
    numbers: bool = True,
    default: object = None,
) -> tuple[int, list]:
    """Generator to synchronize a list of PageContentIterators.

    Args:
        iterators(list): list of `PageContent`-Iterators
        numbers(bool): if True, yield (pagenumber, content)
                       if False, yield content
        default(object): return if no element is given
    Yields:
        pagenumber: (pagenumber, content of current pagenumber)
    """
    # ensure to have sorted iterators
    for index, iterator in enumerate(iterators):
        pages = [determine_pagenumber(item) for item in iterator]
        assert utila.isascending(pages), f'iter: {index} not sorted: {iterator}'
    # avoid side effects
    iterators = [list(item) for item in iterators]
    while any(item for item in iterators):
        pnumber = pagenumber_next(iterators)
        popped = []
        for item in iterators:
            try:
                use = determine_pagenumber(item[0]) == pnumber
            except IndexError:
                use = False
            if use:
                popped.append(item[0])
                item.remove(item[0])
            else:
                popped.append(default)
        popped: tuple = tuple(popped)
        if numbers:
            yield pnumber, popped
        else:
            yield popped


def pagenumber_next(items) -> int:
    result = utila.INF
    for item in items:
        with contextlib.suppress(IndexError):
            result = min((result, determine_pagenumber(item[0])))
    return result


def determine_pagenumber(item) -> int:
    """\
    >>> determine_pagenumber([]) == utila.INF
    True
    """
    if item is None:
        return utila.INF
    with contextlib.suppress(AttributeError):
        return item.page
    with contextlib.suppress(AttributeError):
        return item.number
    return utila.INF


def simplify_pages(numbers: tuple) -> str:
    """\
    >>> simplify_pages(10)
    '10'
    >>> simplify_pages((1, 2, 3, 4, 5))
    '1:6'
    >>> simplify_pages([1, 3, 5, 6, 7])
    '1,3,5:8'
    >>> simplify_pages(None)
    ':'
    >>> simplify_pages((-3, -2, -1, 0, 1, 2))
    '_3:3'
    """
    if not numbers:
        return ':'
    if isinstance(numbers, int):
        numbers = [numbers]
    collected = []
    diffed = utila.groupby_diff(numbers, maxdiff=1)
    for item in diffed:
        if len(item) == 1:
            collected.append(item[0])
        else:
            collected.append(f'{item[0]}:{item[-1]+1}')
    joined = utila.from_tuple(collected, separator=',')
    # replace with special pattern
    result = joined.replace('-', '_')
    return result


class PageGenerator:
    """\
    >>> morepages = PageGenerator(pages_max=10)
    >>> (next(morepages), next(morepages), next(morepages))
    (0, 1, 2)
    >>> [next(morepages) for _ in range(5)]
    [3, 4, 5, 6, 7]
    >>> newpages = PageGenerator(pages=(30, 31, 21, 35, 36, 37))
    >>> list(newpages)
    [21, 30, 31, 35, 36, 37]
    """

    def __init__(self, pages: tuple = None, pages_max: int = 512):
        self.pages = [
            page for page in utila.rlist(pages_max)
            if not utila.should_skip(page, pages)
        ]
        self.pages = iter(self.pages)

    def __iter__(self):
        return self.pages

    def __next__(self):
        return next(self.pages)
