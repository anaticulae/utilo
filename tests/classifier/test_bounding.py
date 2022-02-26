# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import pytest

import utila


@pytest.mark.parametrize('min_elements, expected_groups', [
    (1, 3),
    (2, 1),
])
def test_cluster_common_items_2groups(min_elements, expected_groups):
    example = [
        [((1, 2, 3, 4), '1')],
        [((1, 2, 3, 4), '2')],
        [((1, 2, 3, 4), '3')],
        [((1, 2, 3, 4), '4')],
        [
            ((100, 2, 120, 4), '10'),
            ((10, 2, 15, 4), '2'),
        ],
    ]
    collected = utila.common_items(
        example,
        min_elements=min_elements,
    )
    assert len(collected) == expected_groups, collected


EXAMPLE = [
    12.71, 17.95, 18.98, 4.97, 14.0, 5.52, 13.46, 6.05, 12.93, 6.59, 12.39,
    7.12, 11.86, 7.66, 11.32, 8.19, 10.78, 8.74, 10.24, 9.27, 9.71, 9.81, 9.17,
    10.34, 8.64, 10.88, 8.09, 11.42, 7.56, 11.96, 7.02, 12.49, 6.49, 13.03,
    5.95, 13.56, 5.41, 14.11, 4.87, 14.64, 4.34, 15.18, 3.8, 15.71, 3.27, 16.25,
    2.73, 16.78, 2.19, 17.33, 1.65, 17.86, 1.12, 18.4, 19.51, 18.97, 164.83
]


def test_cluster_max_distance_no_diff():
    unique = utila.make_unique(EXAMPLE)
    clustered = utila.max_distance(
        unique,
        diff=0.0,
        min_elements=1,
    )
    assert len(clustered) == len(unique)


def test_cluster_max_distance():
    unique = sorted(utila.make_unique(EXAMPLE))
    max_diff = 5.0
    clustered = utila.max_distance(
        unique,
        diff=max_diff,
        min_elements=2,
    )
    assert clustered, clustered
    for cluster in clustered:
        mins, maxs = min(cluster), max(cluster)
        diff = math.fabs(mins - maxs)
        assert diff <= max_diff, diff
    assert len(clustered) == 4, clustered
