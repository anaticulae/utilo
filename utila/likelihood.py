# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def uniform_result(items) -> list:
    """Determine ?relatively likelihood? of a collection.

    Args:
        items(list,dict): collection with occurrence of position in collection
    Returns:
        List with relative likelihood of occurrence.
    """
    if isinstance(items, dict):
        return _uniform_dict(items)
    return _uniform_list(items)


def maxi(items, count: int = 1) -> list:
    """Determine the maximized likelihood of an uniformed collection.

    Args:
        items(list,dict): data for determining uniformed data
        count(int): number of possible results
    Returns:
        element(s) with maximized likelihood
    """
    return _max_mini(items, method=max, count=count)


def mini(items, count: int = 1) -> list:
    """Determine the minimized likelihood of an uniformed collection.

    Args:
        items(list,dict): data for determining uniformed data
        count(int): number of possible results
    Returns:
        element(s) with minimized likelihood
    """
    return _max_mini(items, method=min, count=count)


def select_maxi(items, caller=len, count=1):
    selected = _select(items, decider=max, caller=caller, count=count)
    return selected


def _uniform_list(items: list):
    assert isinstance(items, (list, tuple)), type(items)
    assert all(isinstance(item, (int, float)) for item in items)
    features = sum(items)
    if not features:
        return None
    result = [item / features for item in items]
    result = [utila.roundme(item) for item in result]
    return result


def _uniform_dict(items: dict) -> dict:
    values = list(items.values())
    uniformed = _uniform_list(values)
    if uniformed is None:
        return None
    result = dict(zip(items.keys(), uniformed))
    return result


def _max_mini(items, method=max, count: int = 1):
    uniformed = uniform_result(items)
    if uniformed is None:
        return None
    if isinstance(items, dict):
        finding = method(uniformed.values())
        selected = {
            value: occurrence
            for value, occurrence in uniformed.items()
            if occurrence == finding
        }
    else:
        finding = method(uniformed)
        selected = [
            value for value, occurrence in zip(items, uniformed)
            if occurrence == finding
        ]
    if isinstance(selected, list):
        return selected[0:count]
    return selected


def _select(items, decider, caller: callable, count: int):
    # TODO: SUPPORT DICT
    result = []
    items = items[:]  # make a copy to avoid changing the source
    for _ in range(count + 1):
        called = [caller(item) for item in items]
        maximized: list = _max_mini(called, method=decider, count=count)
        # finding
        # XXX: a little bit dirty here
        collected = [
            item for item, selector in zip(items, called)
            if selector in maximized
        ]
        # cluster can contain more than one item, if maxi detect more than
        # one max item. For example: if two cluster have 20 items.
        # TODO: require second judger
        result.extend(collected)
        # remove finding of rest
        for item in collected:
            items.remove(item)
        # stop if no items are left
        if not items:
            break
    return result
