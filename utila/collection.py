# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def make_unique(items):
    """Convert collection where every element exists only once.

    Hint:
        stable algorithm which holds the previous order
    """
    single = Single()
    result = [item for item in items if not single.contains(item)]
    return result


class Single:
    """Ensure to use item only once."""

    def __init__(self):
        self.visited = set()

    def contains(self, item) -> bool:
        """Check if items contains Single container and add item
        afterwards.

        Returns:
            True  if item was already added due contains
            False if item was not added. Add item afterwards
         """
        try:
            hashed = hash(item)
        except TypeError:
            # unhashable
            hashed = hash(str(item))
        if hashed in self.visited:
            return True
        self.visited.add(hashed)
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
