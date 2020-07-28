# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import enum


class MatchStrategy(enum.Enum):
    FIRST = enum.auto()
    MAX = enum.auto()
    MIN = enum.auto()
    LAST = enum.auto()


def match(
        cluster: 'Cluster',
        todo: 'Clusters',
        classifier: callable,
        strategy: MatchStrategy = None,
) -> int:
    decider = match_first
    if strategy == MatchStrategy.LAST:
        decider = match_last
    elif strategy == MatchStrategy.MIN:
        decider = match_min
    elif strategy == MatchStrategy.MAX:
        decider = match_max
    return decider(cluster, todo, classifier)


def match_first(cluster: 'Cluster', todo: 'Clusters', classifier: callable):
    for clusterindex, candiat in enumerate(todo):
        matched = classifier(
            candidat=candiat.center,
            clusteritem=cluster.center,
        )
        if matched is None or matched is False:
            continue
        return clusterindex
    return None


def match_last(cluster: 'Cluster', todo: 'Clusters', classifier: callable):
    result = None
    for clusterindex, candiat in enumerate(todo):
        matched = classifier(
            candidat=candiat.center,
            clusteritem=cluster.center,
        )
        if matched is None or matched is False:
            continue
        result = clusterindex
    return result


def match_min(cluster: 'Cluster', todo: 'Clusters', classifier: callable):
    minvalue = None
    result = None
    for clusterindex, candiat in enumerate(todo):
        matched = classifier(
            candidat=candiat.center,
            clusteritem=cluster.center,
        )
        if matched is None or matched is False:
            continue
        if minvalue is not None and matched >= minvalue:
            continue
        minvalue = matched
        result = clusterindex
    return result


def match_max(cluster: 'Cluster', todo: 'Clusters', classifier: callable):
    maxvalue = None
    result = None
    for clusterindex, candiat in enumerate(todo):
        matched = classifier(
            candidat=candiat.center,
            clusteritem=cluster.center,
        )
        if matched is None or matched is False:
            continue
        if maxvalue is not None and matched <= maxvalue:
            continue
        maxvalue = matched
        result = clusterindex
    return result
