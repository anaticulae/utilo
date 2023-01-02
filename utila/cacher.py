# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
>>> @cacheme
... def complex(item):
...     return str(item)
>>> complex([20, 30])
'[20, 30]'
>>> complex([20, 30]) # invoke cache
'[20, 30]'
>>> cache_clear()
"""

import _thread
import collections
import functools

MAXSIZE = 4096
CACHE_DISABLED = False
CACHES = set()


def cacheme(func=None, maxsize: int = MAXSIZE):

    def decorating_function(user_function):
        wrapper = _lru_cache_wrapper(user_function, maxsize, _CacheInfo)
        CACHES.add(wrapper)
        wrapped = functools.update_wrapper(wrapper, user_function)
        return wrapped

    if func is None:
        # support @cacheme()
        return decorating_function
    # support @cacheme
    return decorating_function(func)


def cache_clear():
    for item in CACHES:
        item.cache_clear()


def cache_disable():
    global CACHE_DISABLED
    CACHE_DISABLED = True


def cache_enable():
    global CACHE_DISABLED
    CACHE_DISABLED = False


def safehash(item):
    """\
    >>> assert safehash([1,2,3])
    """
    try:
        return hash(item)
    except TypeError:
        return hash(str(item))


functools._HashedSeq.__init__.__defaults__ = (safehash,)

# pylint:disable=all

################################################################################
### LRU Cache function decorator
################################################################################

_CacheInfo = collections.namedtuple(
    "CacheInfo",
    ["hits", "misses", "maxsize", "currsize"],
)


def _lru_cache_wrapper(user_function, maxsize, _CacheInfo):  # pragma: no cover
    # Constants shared by all lru cache instances:
    sentinel = object()  # unique object used to signal cache misses
    make_key = functools._make_key  # build a key from the function arguments
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3  # names for the link fields

    cache = {}
    hits = misses = 0
    full = False
    cache_get = cache.get  # bound method to lookup a key or return None
    cache_len = cache.__len__  # get cache size without calling len()
    lock = _thread.RLock()  # because linkedlist updates aren't threadsafe
    root = []  # root of the circular doubly linked list
    root[:] = [root, root, None, None]  # initialize by pointing to self

    def wrapper(*args, **kwds):
        global CACHE_DISABLED
        if CACHE_DISABLED:
            result = user_function(*args, **kwds)
            return result
        # Size limited caching that tracks accesses by recency
        nonlocal root, hits, misses, full
        key = make_key(args, kwds, None)
        with lock:
            link = cache_get(key)
            if link is not None:
                # Move the link to the front of the circular queue
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = root[PREV]
                last[NEXT] = root[PREV] = link
                link[PREV] = last
                link[NEXT] = root
                hits += 1
                return result
            misses += 1
        result = user_function(*args, **kwds)
        with lock:
            if key in cache:
                # Getting here means that this same key was added to the
                # cache while the lock was released.  Since the link
                # update is already done, we need only return the
                # computed result and update the count of misses.
                pass
            elif full:
                # Use the old root to store the new key and result.
                oldroot = root
                oldroot[KEY] = key
                oldroot[RESULT] = result
                # Empty the oldest link and make it the new root.
                # Keep a reference to the old key and old result to
                # prevent their ref counts from going to zero during the
                # update. That will prevent potentially arbitrary object
                # clean-up code (i.e. __del__) from running while we're
                # still adjusting the links.
                root = oldroot[NEXT]
                oldkey = root[KEY]
                oldresult = root[RESULT]
                root[KEY] = root[RESULT] = None
                # Now update the cache dictionary.
                del cache[oldkey]
                # Save the potentially reentrant cache[key] assignment
                # for last, after the root and links have been put in
                # a consistent state.
                cache[key] = oldroot
            else:
                # Put result in a new link at the front of the queue.
                last = root[PREV]
                link = [last, root, key, result]
                last[NEXT] = root[PREV] = cache[key] = link
                # Use the cache_len bound method instead of the len() function
                # which could potentially be wrapped in an lru_cache itself.
                full = (cache_len() >= maxsize)
        return result

    def cache_info():
        """Report cache statistics"""
        with lock:
            return _CacheInfo(hits, misses, maxsize, cache_len())

    def cache_clear():
        """Clear the cache and cache statistics"""
        nonlocal hits, misses, full
        with lock:
            cache.clear()
            root[:] = [root, root, None, None]
            hits = misses = 0
            full = False

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    return wrapper
