# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def determine_cluster(todo, classificator):
    if not todo:
        return []

    # prepare cluster, a single element is a cluster
    result = [[item] for item in todo]

    def match(result, current):
        for clusterindex, cluster in enumerate(result):
            for clusteritem in cluster:
                match = [
                    classificator(candidat=test, clusteritem=clusteritem)
                    for test in current
                ]
                if any(match):
                    return clusterindex
        return None

    def clusterme(result):
        result, todo = result[0], result[1:]
        if not isinstance(result[0], list):
            result = [result]
        while todo:
            current = todo.pop()
            index = match(result, current)
            if index is None:
                # No match, create new cluster
                result.insert(0, current)
            else:
                result[index].extend(current)
        return result

    # Break when cluster does not change result
    # Cluster till cluster move does not change the result
    before = set()
    while True:
        result = clusterme(result)
        hashid = hash(str(result))
        if hashid in before:
            break
        before.add(hashid)

    # A cluster must have at least 2 items
    clusters = [item for item in result if len(item) > 1]
    return clusters


# EXAMPLES:


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

    return determine_cluster(todo, classificator)


def same_area_cluster(todo, max_difference=10.0):

    def classificator(candidat, clusteritem, max_difference=max_difference):
        assert max_difference >= 0.0

        from math import sqrt

        def distance(x0, y0, x1, y1):
            return sqrt(pow((x0 - x1), 2) + pow((y0 - y1), 2))

        def matcher(candidat, clusteritem):
            testbox, _ = candidat
            goalbox, _ = clusteritem
            equality = distance(
                # testbox.x_bottom,
                testbox[0],
                # testbox.y_bottom,
                testbox[1],
                # goalbox.x_bottom,
                goalbox[0],
                # goalbox.y_bottom,
                goalbox[1],
            ) + distance(
                # testbox.x_top,
                testbox[2],
                # testbox.y_top,
                testbox[3],
                # goalbox.x_top,
                testbox[2],
                # goalbox.y_top,
                testbox[3],
            )
            return equality <= max_difference

        return matcher(candidat, clusteritem)

    return determine_cluster(todo, classificator)
