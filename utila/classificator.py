# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import math

from utila.utils import flatten


def common_items(
        collected: list,
        max_difference: float = 10.0,
        min_elements=2,
) -> list:
    """Cluster items due `same_area_cluster`.

    Args:
        collected: items to cluster
        max_difference(float): upper bound of differences which is accepted
                               by classificator as same item.
        min_elements(int): smallest accepted cluster
    Returns:
        list of filtered cluster

    Example:
        [
            [(bounds,item), (bounds,item), (bounds,item)],
            [(bounds,item), (bounds,item)],
            [(bounds,item), (bounds,item), (bounds,item), (bounds,item)],
        ]
    """
    flat = flatten(collected)
    assert all([isinstance(item, tuple) for item in flat]), flat

    clusters = same_area_cluster(
        flat,
        max_difference=max_difference,
        min_elements=min_elements,
    )
    result = [page_from_cluster(cluster, collected) for cluster in clusters]
    return result


def page_from_cluster(cluster, collected):
    result = []
    for pagecount, content in enumerate(collected):
        result.extend([(
            pagecount,
            test,
        ) for test in content if test in cluster])
    return result


def three_side_equal_cluster(todo):

    def classificator(candidat, clusteritem):

        def matcher(candidat, clusteritem):
            candidat_pos, _ = candidat
            cluster_pos, _ = clusteritem

            eqaul = sum([
                abs(first - second) < 0.001  # float difference is allowed
                for (first, second) in zip(candidat_pos, cluster_pos)
            ])
            return eqaul >= 3

        return matcher(candidat, clusteritem)

    return determine_cluster(todo, classificator, min_elements=2)


def same_area_cluster(
        todo,
        max_difference: float = 10.0,
        min_elements: int = 2,
):

    def classificator(candidat, clusteritem, max_difference=max_difference):

        def distance(x0, y0, x1, y1):
            return math.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))

        def matcher(candidat, clusteritem):
            testbox, _ = candidat
            goalbox, _ = clusteritem
            equality = distance(
                testbox[2],
                testbox[3],
                goalbox[2],
                goalbox[3],
            ) + distance(
                testbox[0],
                testbox[1],
                goalbox[0],
                goalbox[1],
            )
            return equality <= max_difference

        return matcher(candidat, clusteritem)

    return determine_cluster(todo, classificator, min_elements=min_elements)


def determine_cluster(todo, classificator, min_elements=2):
    if not todo:
        return []
    # prepare cluster, a single element is a cluster
    result = [[item] for item in todo]
    # Break when cluster does not change result. Cluster till clustering
    # does not change the result.
    before = set()
    while True:
        result = clusterme(result, classificator)
        if len(result) == 1:
            # all elements are in the same group
            break
        hashid = hash(str(result))
        if hashid in before:
            break
        before.add(hashid)
    # A cluster must have at least 2 items
    clusters = [item for item in result if len(item) >= min_elements]
    return clusters


def match(result, current, classificator):
    for index, cluster in enumerate(result):
        for item in cluster:
            result = [
                classificator(candidat=test, clusteritem=item)
                for test in current
            ]
            if any(result):
                return index
    return None


def clusterme(result, classificator):
    result, todo = result[0], result[1:]
    if not isinstance(result[0], list):
        result = [result]
    while todo:
        current = todo.pop()
        index = match(result, current, classificator)
        if index is None:
            # No match, create new cluster
            result.insert(0, current)
        else:
            result[index].extend(current)
    return result
