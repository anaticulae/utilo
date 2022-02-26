# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def test_classifier_same_area_cluster():
    todo = [
        ((0, 0, 50, 50), 'A'),
        ((200, 200, 300, 300), 'B'),
        ((0, 0, 50, 50), 'C'),
        ((250, 250, 300, 300), 'D'),
    ]
    clusters = utila.same_area_cluster(todo, max_difference=0.0)
    clusters = [item[:] for item in clusters]
    expected = [[
        ((0, 0, 50, 50), 'A'),
        ((0, 0, 50, 50), 'C'),
    ]]
    assert clusters == expected


def test_classifier_three_side_equal():
    todo = [
        ((0, 0, 50, 50), 'A'),
        ((0, 0, 100, 50), 'B'),
        ((0, 0, 25, 50), 'C'),
        ((0, 0, 200, 50), 'D'),
        ((200, 200, 250, 250), 'E'),
    ]
    clusters = utila.three_side_equal_cluster(todo)
    expected = [[
        ((0, 0, 50, 50), 'A'),
        ((0, 0, 100, 50), 'B'),
        ((0, 0, 25, 50), 'C'),
        ((0, 0, 200, 50), 'D'),
    ]]
    assert len(clusters) == len(expected), clusters
    sorted_result = sorted(clusters[0], key=lambda item: item[1])
    assert sorted_result == expected[0], sorted_result


def test_intersecting_line_cluster(thousand_lines):
    clustered = utila.intersecting_line_cluster(thousand_lines)
    assert len(clustered) == 1
