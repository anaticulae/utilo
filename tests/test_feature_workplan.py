# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import tests.examples.workplan.multistep
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
    utila.create_step(
        'fourth',
        [
            utila.ResultFile(producer='A', name='a'),
            utila.ResultFile(producer='A', name='b'),
            utila.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
    utila.create_step(
        'fifth',
        [
            utila.ResultFile(producer='A', name='a'),
            utila.ResultFile(producer='A', name='b'),
            utila.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
]


def test_parallelize_workplan_order():
    # 3 level's
    process_and_separator = f'{PROCESS}{utila.feature.REQUIREMENT_SEPARATOR}'
    order = utila.feature.input_order(PLAN, root=PROCESS)
    expected = [
        [
            f'{process_and_separator}fifth',
            f'{process_and_separator}first',
            f'{process_and_separator}fourth',
        ],
        [f'{process_and_separator}third'],
        [f'{process_and_separator}second'],
    ]
    assert len(order) == 3, utila.log_raw(order)
    assert order == expected, utila.log_raw(order)


def test_parallelize_workplan():
    # 3 level
    single_processed = utila.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=1,
    )
    assert len(single_processed) == 5, str(single_processed)

    # multilevel limited by required resoure
    multi_processed = utila.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=10,
    )
    assert len(multi_processed) == 3, str(multi_processed)

    # multilevel limited by required resoure and limited by cores
    multi_processed = utila.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=2,
    )
    assert len(multi_processed) == 4, str(multi_processed)


def test_feature_resultfile_ctor_position():
    expected = utila.ResultFile(producer='abc', name='def')
    assert utila.ResultFile('abc', 'def') == expected


def test_parallelize_workplan_multiprocessing():
    """Test to ensure that parallelizing works with multi resource
    environment. This is an old example wich failed before."""
    example = tests.examples.workplan.multistep.WORKPLAN
    root = tests.examples.workplan.multistep.ROOT

    parallelized = utila.parallelize_workplan(
        example,
        root=root,
        max_processes=20,
    )

    assert len(parallelized) == 2, utila.log_raw(parallelized)
    assert len(parallelized[0]) == 5, utila.log_raw(parallelized[0])
    assert len(parallelized[1]) == 1, utila.log_raw(parallelized[1])
