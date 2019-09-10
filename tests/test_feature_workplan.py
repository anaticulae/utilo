# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila
import utila.feature

# TODO: REMOVE COPY AND PASTE, MOVE EXAMPLES TO REGULAR PYTHON FILES

PROCESS = 'process'
PLAN = [
    utila.create_step(
        'second',
        [
            utila.ResultFile(producer=PROCESS, name='third_result'),
            utila.ResultFile(producer='first', name='b'),
            utila.ResultFile(producer='B', name='c'),
        ],
        ('result',),
    ),
    utila.create_step(
        'third',
        [
            utila.ResultFile(producer=PROCESS, name='first_result'),
            utila.ResultFile(producer=PROCESS, name='b_b'),
        ],
        ('result',),
    ),
    utila.create_step(
        'first',
        [
            utila.ResultFile(producer='A', name='a'),
            utila.ResultFile(producer='A', name='b'),
            utila.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
]


def test_parallelize_workplan_order():
    # 2 level's
    order = utila.feature.input_order(PLAN)
    assert len(order) == 2, str(order)


def test_parallelize_workplan():
    # 3 level
    single_processed = utila.parallelize_workplan(PLAN, 1)
    assert len(single_processed) == 3, str(single_processed)

    # multilevel limited by required resoure
    multi_processed = utila.parallelize_workplan(PLAN, 10)
    assert len(multi_processed) == 2, str(multi_processed)


def test_feature_resultfile_ctor_position():
    expected = utila.ResultFile(producer='abc', name='def')
    assert utila.ResultFile('abc', 'def') == expected
