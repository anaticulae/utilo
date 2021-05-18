# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utila
import utila.classifier.base
import utila.classifier.strategy


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


def three_side_equal_cluster(
    todo,
    min_elements: int = 2,
    max_diff=2.0,
    selector=None,
):
    selector = selector if selector else lambda x: x[0]

    def classifier(candidat, clusteritem):

        def matcher(candidat, clusteritem):
            bounding_cluster = selector(clusteritem)
            bounding_test = selector(candidat)

            equal = sum([
                utila.near(first, second, diff=max_diff)
                for (first, second) in zip(bounding_test, bounding_cluster)
            ])
            return equal >= 3

        return matcher(candidat, clusteritem)

    return utila.classifier.base.determine_cluster(
        todo,
        classifier,
        min_elements=min_elements,
    )


def same_area_cluster(
    todo,
    max_difference: float = 10.0,
    min_elements: int = 2,
    selector=None,
):
    selector = selector if selector else lambda x: x[0]

    def classifier(candidat, clusteritem, max_difference=max_difference):

        def matcher(candidat, clusteritem):
            testbox = selector(candidat)
            goalbox = selector(clusteritem)
            equality = utila.norm(
                testbox[2],
                testbox[3],
                goalbox[2],
                goalbox[3],
            ) + utila.norm(
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
    max_diff: float = 10.0,
    min_elements: int = 1,
    matcher: callable = None,
):
    """\
    >>> len(same_line_cluster([(0, 50, 100, 55), (70, 49, 140, 52), (0, 400, 100, 401)]))
    2
    """
    if not matcher:
        matcher = lambda bounding: bounding[3]

    def classifier(candidat, clusteritem):
        return utila.near(
            matcher(candidat),
            matcher(clusteritem),
            diff=max_diff,
        )

    return utila.determine_cluster(todo, classifier, min_elements=min_elements)


def intersecting_rectangle_cluster(
    todo,
    min_elements: int = 1,
    bounding: callable = None,
):
    bounding = bounding if bounding else lambda item: item

    def classifier(candidat, clusteritem):
        return utila.intersecting_rectangle(
            bounding(candidat),
            bounding(clusteritem),
        )

    return utila.determine_cluster(
        todo,
        classifier,
        min_elements=min_elements,
        strategy=utila.classifier.strategy.MatchStrategy.ANY,
    )


def intersecting_line_cluster(todo, min_elements: int = 1):

    def classifier(candidat, clusteritem):
        return utila.intersecting_lines(candidat, clusteritem)

    return utila.determine_cluster(
        todo,
        classifier,
        min_elements=min_elements,
        strategy=utila.classifier.strategy.MatchStrategy.ANY,
    )
