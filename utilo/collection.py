# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import math
import random

import utilo


def unique(items, converter: callable = None):
    """Convert collection where every element exists only once.

    >>> unique((1, 2, 3, 3, 4, 5, 1))
    [1, 2, 3, 4, 5]

    Hint:
        stable algorithm which holds the previous order
    """
    single = Single(converter=converter)
    result = [item for item in items if not single.contains(item)]
    return result


def partition(key, items):
    """\
    >>> partition(key=None, items=(1, 2, 3))
    ((1, 2, 3), [])
    >>> partition(lambda x: x%2 == 0, [1, 2, 3, 4, 5])
    ([2, 4], [1, 3, 5])
    """
    matched = []
    not_matched = []
    if key is None:
        return items[:], []
    for item in items:
        if key(item):
            matched.append(item)
        else:
            not_matched.append(item)
    return matched, not_matched


def choose_random(
    items,
    count: int = 5,
    repeat: bool = False,
    seed: float = None,
) -> list:
    """Chose `count` random items of a collection

    >>> choose_random((5, 5, 5, 5, 5, 5), count=2)
    [5, 5]
    >>> choose_random((1, 2, 3), count=7, repeat=True, seed=0.5)
    [1, 3, 2, 1, 1, 1, 3]
    >>> choose_random((1,2,3), count=10, seed=0.5)
    [1, 3, 2]

    Hint:
        This process does not change the source collection. There are no
        side effects.
    Args:
        items(list): data collection to select random items
        count(int): number of items to return
        repeat(bool): if True, count can be higher than items-len
        seed(float): random seed
    Returns:
        `count` selected items out of collections
    """
    # items = list(items)  # TODO: create a copy???
    if not repeat and len(items) < count:
        count = len(items)
    generator = random
    if seed is not None:
        generator: 'Random' = random.Random(seed)  # nosec
    return generator.choices(items, k=count)


def split_shuffle(items, length, seed=0.0):
    """Split collection into two lists and shuffle data.

    >>> split_shuffle([0, 1, 2, 3, 4, 5], length=0.3, seed=5.0)
    ([1, 0], [3, 5, 2, 4])
    """
    # avoid side effects
    items = items[:]
    generator: 'Random' = random.Random(seed)  # nosec
    generator.shuffle(items)
    left = items[0:math.ceil(len(items) * length)]
    right = items[len(left):]
    return left, right


def splitby_count(items, count) -> tuple:
    """\
    >>> splitby_count('hello my friend this is smart', (3, 5, 9))
    ['hel', 'lo my', ' friend t', 'his is smart']
    >>> splitby_count('Hello', (5, ))
    ['Hello']
    """
    assert utilo.iterable(count), count
    result = []
    index = 0
    for part in count:
        selected = items[index:index + part]
        result.append(selected)
        index += part
    rest = items[index:]
    if rest:
        result.append(rest)
    return result


def chunks(items, size: int = 1) -> list:
    """\
    >>> chunks((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), size=3)
    [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10,)]
    >>> chunks([1, 2, 3], size=10)
    [[1, 2, 3]]
    >>> chunks([1, 2, 3], size=1)
    [[1], [2], [3]]
    """
    result = []
    for index in range(math.ceil(len(items) / size)):
        result.append(items[index * size:(index + 1) * size])
    return result


class Single(contextlib.ContextDecorator):
    """Ensure to use item only once.

    >>> container = Single()
    >>> container.contains(1, mark=False)
    False
    >>> container.contains(1, mark=True)
    False
    >>> container.contains(1)
    True
    >>> 1 in container
    True
    >>> with Single() as single:
    ...     1 in single
    ...     1 in single
    ...     1 in single
    False
    True
    True
    """

    def __init__(self, converter: callable = None):
        self.converter = utilo.scall_or_me(converter)
        self.visited = set()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass

    def contains(self, item: object, mark: bool = True) -> bool:
        """Check if items contains Single container and add item
        afterwards.

        Args:
            item(object): data to verify
            mark(bool): if True add to visited list
        Returns:
            True  if item was already added due contains
            False if item was not added. Add item afterwards
        """
        item = self.converter(item)
        try:
            # Try that hashing is possible. We do not store hash value
            # cause -1 and -2 can have the same hash value.
            hash(item)
        except TypeError:
            # unhashable, str is always hashable
            item = hash(str(item))
        if item in self.visited:
            return True
        if mark:
            self.visited.add(item)
        return False

    def __contains__(self, item):
        return self.contains(item)


class Buckets:
    """Fill items depending on values into upper limit buckets.

    >>> bucket = Buckets((50, 100, 400), sorting=True)
    >>> for item in (70, 85, 500, 130, 100):
    ...    bucket.add(item)
    >>> list(bucket)
    [[], [70, 85], [100, 130], [500]]
    >>> bucket = Buckets((50, 100, 400), sorting=False)
    >>> for item in (70, 85, 500, 130, 100):
    ...    bucket.add(item)
    >>> bucket[0], bucket[1]
    ([], [70, 85])
    >>> bucket.add(1000)


    Possible selector:
        selector=operator.attrgetter('y1')
    """

    def __init__(self, border, selector=None, sorting: bool = False):
        self.sorting = sorting
        self.selector = utilo.scall_or_me(selector)
        self.border = [
            item if utilo.isnumber(item) else self.selector(item)
            for item in border
        ]
        self.border.append(utilo.INF)

        self.bucket = [[] for _ in range(len(self.border))]

    def add(self, item):
        for border, bucket in zip(self.border, self.bucket):
            if self.selector(item) >= border:
                continue
            bucket.append(item)
            break

    def __getitem__(self, index):
        data = self.bucket[index]
        if not self.sorting:
            return data
        return sorted(data, key=self.selector)

    def __len__(self):
        return len(self.bucket)


def dicts_united(*items):
    """\
    >>> dicts_united({'first': 10}, {'second': 20})
    {'first': 10, 'second': 20}
    >>> dicts_united({'first': 10}, {'second': 20}, {'second': 15})
    {'first': 10, 'second': 15}
    >>> dicts_united({}, {})
    {}
    """
    result = {}
    for item in items:
        if not item:
            # skip empty dict
            continue
        result.update(item)
    return result


def dict_reverse(dictum):
    """\
    >>> dict_reverse(dict(first='Helmut', second=10))
    {'Helmut': 'first', 10: 'second'}
    """
    return {value: key for key, value in dictum.items()}


class CasedSet:
    """Wrapper that lower case input data to verify if data is present.

    >>> data = CasedSet('Helm melm GELM'.split())
    >>> assert 'HELM' in data
    >>> assert len(list(data)) == 3
    >>> assert data | data
    >>> sorted(data | {'hello'})
    ['gelm', 'hello', 'helm', 'melm']
    """

    def __init__(self, values, method=str.lower):
        self.method = method
        self.values = frozenset([self.method(item) for item in values])

    def __iter__(self):
        return iter(self.values)

    def __contains__(self, item):
        return self.method(item) in self.values

    def __or__(self, items):
        if isinstance(items, CasedSet):
            items: frozenset = items.values
        return CasedSet(self.values | items, method=self.method)


class LowerCasedSet(CasedSet):
    pass


class UpperCasedSet(CasedSet):
    """\
    >>> data = UpperCasedSet('helm telm melm'.split())
    >>> assert 'HELM' in data
    >>> list(data)
    ['HELM', 'TELM', 'MELM']
    """

    def __init__(self, values):
        super().__init__(values, method=str.upper)


def starmap(items) -> list:
    """\
    >>> starmap([5,])
    [[5]]
    >>> starmap(([1,], [2,]))
    [[1, 2]]
    >>> starmap([[1, 2], [3,]])
    [[1, 3], [2, 3]]
    >>> starmap([(1, 2, 3), (4, ), (5, 6)])
    [[1, 4, 5], [2, 4, 5], [3, 4, 5], [1, 4, 6], [2, 4, 6], [3, 4, 6]]
    >>> starmap([[0], [0.0], [0.0], [0], [0.0], [0.0]])
    [[0, 0.0, 0.0, 0, 0.0, 0.0]]
    """
    if len(items) == 1:
        return [items]
    result = items[0]
    for item in items[1:]:
        result = twice(result, item)
    return result


def twice(firsts, seconds):
    """\
    >>> twice([2], [1])
    [[2, 1]]
    >>> twice([1, 3], [2, 4, 6, 8])
    [[1, 2], [3, 2], [1, 4], [3, 4], [1, 6], [3, 6], [1, 8], [3, 8]]
    >>> twice([[1, 2, 3], 3], [2, 4, 6, 8])
    [[1, 2, 3, 2], [3, 2], [1, 2, 3, 4], [3, 4], [1, 2, 3, 6], [3, 6], [1, 2, 3, 8], [3, 8]]
    """
    # TODO: ADD DOCS HERE
    result = []
    for second in seconds:
        for first in firsts:
            if utilo.iterable(first):
                result.append(list(first) + [second])
            else:
                result.append([first] + [second])
    return result


def minimal(items) -> list:
    """\
    >>> minimal(([1,], [2,]))
    [[1, 2]]
    >>> minimal([[1, 2], [3,]])
    [[1, 3], [2, 3]]
    >>> minimal([(1, 2, 3), (4, ), (5, 6)])
    [[1, 4, 5], [2, 4, 6], [3, 4, 6]]
    >>> minimal([(4, ), (1, 2, 3), (5, 6)])
    [[4, 1, 5], [4, 2, 6], [4, 3, 6]]
    >>> minimal([(1, 3, 6), (2, 4, 7), (9, 0, 8)])
    [[1, 2, 9], [3, 4, 0], [6, 7, 8]]
    """
    todo = [len(item) for item in items]
    current = [0] * len(items)
    result = []
    while sum(todo) != sum(current):  # pylint:disable=W0149
        step = []
        for pos, _ in enumerate(items):
            if current[pos] < todo[pos]:
                step.append(items[pos][current[pos]])
                current[pos] += 1
            else:
                step.append(items[pos][current[pos] - 1])
        result.append(step)
    return result


def first_one(items) -> list:
    """\
    >>> first_one(([1,], [2,]))
    [[1, 2]]
    >>> first_one([[1, 2], [3,]])
    [[1, 3], [2, 3]]
    >>> first_one([(4, ), (1, 2, 3), (5, 6)])
    [[4, 1, 5], [4, 2, 5], [4, 3, 5], [4, 1, 6]]
    """
    items = [list(item) for item in items]
    result = []
    for index, _ in enumerate(items):
        base = [item[0] for item in items]
        for current in items[index]:
            copy = list(base)
            copy[index] = current
            result.append(copy)
    result = utilo.make_unique(result)
    return result


def counts(items: list, selector: callable) -> int:
    """\
    >>> counts('ABCAD', lambda x: x == 'A')
    2
    """
    counted = len([item for item in items if selector(item)])
    return counted


def sort_both(
    firsts,
    seconds,
    key: callable = None,
    reverse: bool = False,
) -> tuple:
    """\
    >>> sort_both([5, 1, 3, 10], 'Konrad Frank Theodor Elsa'.split())
    ([1, 3, 5, 10], ['Frank', 'Theodor', 'Konrad', 'Elsa'])
    """
    assert len(firsts) == len(seconds), f'{len(firsts)} == {len(seconds)}'
    merged = list(zip(firsts, seconds))
    key = utilo.scall_or_me(key)
    # x[0] first column
    merged.sort(key=lambda x: key(x[0]), reverse=reverse)  # pylint:disable=C3001
    firsts = [item[0] for item in merged]
    seconds = [item[1] for item in merged]
    return firsts, seconds
