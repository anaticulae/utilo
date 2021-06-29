# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import random

import utila


def make_unique(items):
    """Convert collection where every element exists only once.

    Hint:
        stable algorithm which holds the previous order
    """
    single = Single()
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


def choose_random(items, count: int = 5) -> list:
    """Chose `count` random items of a collection

    >>> choose_random((5, 5, 5, 5, 5, 5), count=2)
    [5, 5]

    Hint:
        This process does not change the source collection. There are no
        side effects.
    Args:
        items(list): data collection to select random items
        count(int): number of items to return
    Returns:
        `count` selected items out of collections
    """
    items = list(items)  # create a copy
    random.shuffle(items)
    return items[0:count]


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


class Single:
    """Ensure to use item only once.

    >>> container = Single()
    >>> container.contains(1, mark=False)
    False
    >>> container.contains(1, mark=True)
    False
    >>> container.contains(1)
    True
    """

    def __init__(self):
        self.visited = set()

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
        try:
            # Try that hashing is possible. We do not store hash value
            # cause -1 and -2 can have the same hash value.
            hash(item)
        except TypeError:
            # unhashable, str is always hashable
            item = str(item)
        if item in self.visited:
            return True
        if mark:
            self.visited.add(item)
        return False


class Buckets:
    """Fill items depending on values into upper limit buckets.

    >>> bucket = Buckets((50, 100, 400), sorting=True)
    >>> for item in (70, 85, 500, 130, 100):
    ...    bucket.add(item)
    >>> list(bucket)
    [[], [70, 85], [100, 130], [500]]

    Possible selector:
        selector=operator.attrgetter('y1')
    """

    def __init__(self, border, selector=None, sorting: bool = False):
        self.sorting = sorting
        self.selector = selector if selector else lambda x: x

        self.border = [self.selector(item) for item in border]
        self.border.append(utila.INF)

        self.bucket = [[] for _ in range(len(self.border))]

    def add(self, item):
        for border, bucket in zip(self.border, self.bucket):
            if self.selector(item) >= border:
                continue
            bucket.append(item)
            return

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
    """
    result = {}
    for item in items:
        result.update(item)
    return result


def dict_reverse(dictum):
    """\
    >>> dict_reverse(dict(first='Helmut', second=10))
    {'Helmut': 'first', 10: 'second'}
    """
    return {value: key for key, value in dictum.items()}


class LowerCasedSet:
    """Wrapper that lower case input data to verify if data is present.

    >>> data = LowerCasedSet('Helm melm GELM'.split())
    >>> assert 'HELM' in data
    >>> assert len(list(data)) == 3
    >>> assert data | data
    """

    def __init__(self, values):
        self.values = frozenset([item.lower() for item in values])

    def __iter__(self):
        return iter(self.values)

    def __contains__(self, item):
        return item.lower() in self.values

    def __or__(self, items):
        if isinstance(items, LowerCasedSet):
            items: frozenset = items.values
        return LowerCasedSet(self.values | items)
