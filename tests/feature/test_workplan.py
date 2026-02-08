# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import tests.examples.workplan.groupme
import tests.examples.workplan.multistep
import tests.examples.workplan.resources
import utilo
import utilo.feature
import utilo.feature.workplan

# utilo.refactor(major=3, description='move examples to separate files')

PROCESS = 'process'
PLAN = [
    utilo.create_step(
        'second',
        [
            utilo.ResultFile(producer=PROCESS, name='third_result'),
            utilo.ResultFile(producer='first', name='b'),
            utilo.ResultFile(producer='B', name='c'),
        ],
        ('result',),
    ),
    utilo.create_step(
        'third',
        [
            utilo.ResultFile(producer=PROCESS, name='first_result'),
            utilo.ResultFile(producer=PROCESS, name='b_b'),
        ],
        ('result',),
    ),
    utilo.create_step(
        'first',
        [
            utilo.ResultFile(producer='A', name='a'),
            utilo.ResultFile(producer='A', name='b'),
            utilo.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
    utilo.create_step(
        'fourth',
        [
            utilo.ResultFile(producer='A', name='a'),
            utilo.ResultFile(producer='A', name='b'),
            utilo.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
    utilo.create_step(
        'fifth',
        [
            utilo.ResultFile(producer='A', name='a'),
            utilo.ResultFile(producer='A', name='b'),
            utilo.ResultFile(producer='A', name='c'),
        ],
        ('result',),
    ),
]


def test_parallelize_workplan_order():
    # 3 level's
    process_and_separator = f'{PROCESS}{utilo.feature.workplan.REQUIREMENT_SEPARATOR}'
    order = utilo.feature.workplan.input_order(PLAN, root=PROCESS)
    expected = [
        [
            f'{process_and_separator}fifth',
            f'{process_and_separator}first',
            f'{process_and_separator}fourth',
        ],
        [f'{process_and_separator}third'],
        [f'{process_and_separator}second'],
    ]
    assert len(order) == 3, utilo.log_raw(order)
    assert order == expected, utilo.log_raw(order)


def test_parallelize_workplan():
    # 3 level
    single_processed = utilo.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=1,
    )
    assert len(single_processed) == 5, str(single_processed)

    # multilevel limited by required resource
    multi_processed = utilo.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=10,
    )
    assert len(multi_processed) == 3, str(multi_processed)

    # multilevel limited by required resource and limited by cores
    multi_processed = utilo.parallelize_workplan(
        PLAN,
        root=PROCESS,
        max_processes=2,
    )
    assert len(multi_processed) == 4, str(multi_processed)


def test_feature_resultfile_ctor_position():
    expected = utilo.ResultFile(producer='abc', name='def')
    assert utilo.ResultFile('abc', 'def') == expected


def test_parallelize_workplan_multiprocessing():
    """Test to ensure that parallelizing works with multi resource
    environment. This is an old example which failed before."""
    example = tests.examples.workplan.multistep.WORKPLAN
    root = tests.examples.workplan.multistep.ROOT

    parallelized = utilo.parallelize_workplan(
        example,
        root=root,
        max_processes=20,
    )

    assert len(parallelized) == 2, utilo.log_raw(parallelized)
    assert len(parallelized[0]) == 5, utilo.log_raw(parallelized[0])
    assert len(parallelized[1]) == 1, utilo.log_raw(parallelized[1])


@pytest.mark.parametrize('max_processes, expected_steps', [
    (6, 1),
    (1, 6),
    (3, 2),
])
def test_parallelize_workplan_pdf_resources(max_processes, expected_steps):
    """Ensure that parallelizing workplan with resources as input works"""
    example = tests.examples.workplan.resources.WORKPLAN
    root = tests.examples.workplan.resources.ROOT

    workplan = utilo.parallelize_workplan(
        example,
        root=root,
        max_processes=max_processes,
    )
    assert len(workplan) == expected_steps, utilo.log_raw(workplan)


def test_parallelize_workplan_groupme():
    """Ensure that parallelizing workplan with resources as input works"""
    example = tests.examples.workplan.groupme.WORKPLAN
    root = tests.examples.workplan.groupme.ROOT

    expected = [
        ['chapter', 'pagenumbers', 'toc'],
        ['footer'],
    ]

    workplan = utilo.parallelize_workplan(
        example,
        root=root,
        max_processes=4,
    )
    assert len(workplan) == 2, utilo.log_raw(workplan)

    workplan = [[item.name for item in step] for step in workplan]
    assert workplan == expected, utilo.log_raw(workplan)


def test_feature_input_order():
    """Test to remove common path's for correct requirement determination."""
    plan_with_path = tests.examples.workplan.groupme.PLAN_WITH_PATH
    root = tests.examples.workplan.groupme.ROOT
    order = utilo.feature.workplan.input_order(plan_with_path, root)
    assert len(order) == 2, utilo.log_raw(order)
    assert len(order[0]) == 3, utilo.log_raw(order)
    assert len(order[1]) == 1, utilo.log_raw(order)


def test_reserved_workstep_names():
    """Do not allow reserved workstep names."""
    with pytest.raises(AssertionError):
        utilo.create_step('all')


def test_workplan_prepare_variables_invalid_datatype():
    variables = [
        utilo.Value(name='valid', typ=int, defaultvar=10),
        utilo.Value(name='on', typ=bool, defaultvar=True),
    ]
    args = {'valid': 'not an int', 'on': 'False'}
    prepared = utilo.feature.workplan.prepare_variables(variables, args)
    assert prepared == [False], prepared


def test_workplan_prepare_outputs_invalid_outputs():
    with pytest.raises(SystemExit):
        utilo.feature.workplan.prepare_outputs(
            process='rawmaker',
            stepname='stepname',
            prefix='oneline',
            outputs=[20, 50],
            outspace='outspace',
        )
