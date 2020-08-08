# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utila
import utila.classifier.base


def common_items(
        collected: list,
        max_difference: float = 10.0,
        min_elements=2,
        selector=None,
) -> list:
    """Cluster items due `same_area_cluster`.

    Hint: The number returning in cluster result, names the number of
    passed data container. Keep this in mind when passing non zero
    indexed data.

    Args:
        collected: items to cluster
        max_difference(float): upper bound of differences which is accepted
                               by classifier as same item.
        min_elements(int): smallest accepted cluster
        selector(callable): select property to cluster
    Returns:
        list of filtered cluster

    Example:
        [
            [(bounds,item), (bounds,item), (bounds,item)],
            [(bounds,item), (bounds,item)],
            [(bounds,item), (bounds,item), (bounds,item), (bounds,item)],
        ]
    """
    assert min_elements >= 1, str(min_elements)
    selector = selector if selector else lambda x: x[0]
    flat = utila.flatten(collected)
    assert all([selector(item) is not None for item in flat]), flat

    clusters = same_area_cluster(
        flat,
        max_difference=max_difference,
        min_elements=min_elements,
        selector=selector,
    )

    def page_from_cluster(cluster, collected) -> list:
        result = []
        for pagecount, content in enumerate(collected):
            result.extend([(
                pagecount,
                test,
            ) for test in content if test in cluster])
        return result

    result = [page_from_cluster(cluster, collected) for cluster in clusters]
    return result


def max_distance(items, diff: float = 1.0, min_elements=2):

    def classifier(candidat, clusteritem):
        return math.fabs(candidat - clusteritem) <= diff

    return utila.classifier.base.determine_cluster(
        items,
        classifier=classifier,
        min_elements=min_elements,
    )


def three_side_equal_cluster(todo):

    def classifier(candidat, clusteritem):

        def matcher(candidat, clusteritem):
            candidat_pos, _ = candidat
            cluster_pos, _ = clusteritem

            eqaul = sum([
                abs(first - second) < 0.001  # float difference is allowed
                for (first, second) in zip(candidat_pos, cluster_pos)
            ])
            return eqaul >= 3

        return matcher(candidat, clusteritem)

    return utila.classifier.base.determine_cluster(
        todo,
        classifier,
        min_elements=2,
    )


def same_area_cluster(
        todo,
        max_difference: float = 10.0,
        min_elements: int = 2,
        selector=None,
):
    selector = selector if selector else lambda x: x[0]

    def classifier(candidat, clusteritem, max_difference=max_difference):

        def distance(x0, y0, x1, y1):
            return math.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))

        def matcher(candidat, clusteritem):
            testbox = selector(candidat)
            goalbox = selector(clusteritem)
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

    return utila.classifier.base.determine_cluster(
        todo,
        classifier,
        min_elements=min_elements,
    )


def same_line_cluster(
        todo,
        max_difference: float = 10.0,
        min_elements: int = 1,
):

    def classifier(candidat, clusteritem, max_difference=max_difference):

        def matcher(candidat, clusteritem):
            diff = math.fabs(candidat.y1 - clusteritem.y1)
            return diff <= max_difference

        return matcher(candidat, clusteritem)

    return utila.determine_cluster(todo, classifier, min_elements=min_elements)
