# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila
import utila.feature.workplan


def test_workplan_prepare_variables_invalid_datatype():
    variables = [
        utila.Value(name='valid', typ=int, defaultvar=10),
        utila.Value(name='on', typ=bool, defaultvar=True),
    ]
    args = {'valid': 'not an int', 'on': 'False'}
    prepared = utila.feature.workplan.prepare_variables(variables, args)
    assert prepared == [False], prepared


def test_workplan_prepare_outputs_invalid_outputs():
    with pytest.raises(SystemExit):
        utila.feature.workplan.prepare_outputs(
            process_='rawmaker',
            stepname='stepname',
            prefix='oneline',
            outputs=[20, 50],
            outspace='outspace',
        )
