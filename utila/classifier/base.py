# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing

import utila
import utila.classifier.strategy


class Cluster:

    def __init__(self, item):
        self.content = [item] if item is not None else []
        self.changed = True

    def extend(self, cluster):
        self.content.extend(cluster.content)
        self.changed = True

    @property
    def center(self):
        if self.changed:
            self.update()
            self.changed = False
        return self.content[0]

    def update(self):
        pass

    def __len__(self):
        return len(self.content)

    def __getitem__(self, index):
        return self.content[index]


Clusters = typing.List[Cluster]


def determine_cluster(
    todo: list,
    classifier: callable,
    min_elements: int = 2,
    ctor: Cluster = None,
    strategy: 'MatchStrategy' = None,
    key: callable = None,
) -> Clusters:
    """Determine cluster out of `todo`.

    Sort clustered result by length of cluster descending.

    Args:
        todo: items to cluster
        classifier: determine if two elements are in the same cluster
        min_elements: min size of valid cluster
        ctor: use different classes to represent cluster
        strategy: use different strategies to select the right cluster
        key: sort items of cluster before returning them
    Returns:
        List of clusters.
    """
    assert min_elements >= 1, str(min_elements)
    if strategy is None:
        strategy = utila.classifier.strategy.MatchStrategy.FIRST
    if not todo:
        return []
    if ctor is None:
        ctor = Cluster
    # prepare cluster, a single element is a cluster
    result = [ctor(item) for item in todo]
    # Break when cluster does not change result
    # Cluster till cluster move does not change the result
    single = utila.Single()
    while True:
        result = clusterme(result, classifier=classifier, strategy=strategy)
        if len(result) == 1:
            # all elements are in the same group
            break
        if single.contains(result):
            break
    # A cluster must have at least 2 items
    clusters = [item for item in result if len(item) >= min_elements]
    if key:
        clusters = [sorted(cluster, key=key) for cluster in clusters]
    clusters = sorted(clusters, key=len, reverse=True)
    return clusters


def clusterme(
    clusters: Clusters,
    classifier: callable,
    strategy: 'MatchStrategy' = None,
) -> Clusters:
    current, todo = clusters[0], clusters[1:]
    result = [current]
    while todo:
        test = todo.pop()
        index = utila.classifier.strategy.match(
            test,
            result,
            classifier,
            strategy=strategy,
        )
        if index is None:
            # No match, create new cluster
            result.insert(0, test)
        else:
            result[index].extend(test)
    return result
