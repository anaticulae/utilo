# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
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


def maxi(items) -> list:
    """Determine the maximized likelihood of an uniformed collection.

    Args:
        items(list,dict): data for determining uniformed data
    Returns:
        element(s) with maximized likelihood
    """
    return _max_mini(items, method=max)


def mini(items) -> list:
    """Determine the minimized likelihood of an uniformed collection.

    Args:
        items(list,dict): data for determining uniformed data
    Returns:
        element(s) with minimized likelihood
    """
    return _max_mini(items, method=min)


def _uniform_list(items: list):
    assert isinstance(items, (list, tuple)), type(items)
    assert all([isinstance(item, (int, float)) for item in items])
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
    result = {key: value for key, value in zip(items.keys(), uniformed)}
    return result


def _max_mini(items, method=max):
    uniformed = uniform_result(items)
    if uniformed is None:
        return None
    if isinstance(items, dict):
        finding = method(uniformed.values())
        selected = {
            value: occurence
            for value, occurence in uniformed.items()
            if occurence == finding
        }
    else:
        finding = method(uniformed)
        selected = [
            value for value, occurence in zip(items, uniformed)
            if occurence == finding
        ]
    if len(selected) == 1 and isinstance(selected, list):
        return selected[0]
    return selected
