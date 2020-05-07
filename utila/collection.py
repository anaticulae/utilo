# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


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
