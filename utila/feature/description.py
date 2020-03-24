# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import textwrap

import utila
import utila.feature


def prepare_description(name: str, description: str, workplan: list) -> str:
    """Create help description with in- and outports for program steps.

    Args:
        name(str): application name
        description(str): text which is presented in --help view
        workplan(list): list of WorkingStep's
    Returns:
        Prepared description with out- and input-parameter.
    """
    result = []
    for step in workplan:
        result.append(f'//{step.name}')
        # prepare inputs
        inputs = format_inputs(step)
        result.append(inputs)
        # prepare outputs
        outputs = format_outputs(step, name)
        result.append(outputs)
        result.append('')
    raw = utila.NEWLINE.join(result)
    return description + utila.NEWLINE + raw


def format_inputs(step) -> str:
    inputs = []
    for source in step.inputs:
        if isinstance(source, utila.feature.Value):
            # for example: <class 'float'>
            datatype = str(source.typ).split("'")[1]
            msg = f'{source.name}({datatype})={source.defaultvar}'
            inputs.append(msg)
        elif isinstance(source, utila.feature.ResultFile):
            inputs.append(f'{source}')
        else:
            try:
                fname, fending = source
            except ValueError:
                fname, fending = source, 'yaml'
            inputs.append(f'{fname}.{fending}')
    inputs = sorted(inputs)
    raw = ''.join('+%s   ' % item.ljust(30, ' ') for item in inputs)
    raw = textwrap.fill(raw, 132)
    return raw


def format_outputs(step, name) -> str:
    outputs = []
    for dest in step.outputs:
        try:
            fname, fending = dest
        except ValueError:
            fname, fending = dest, 'yaml'
        outputs.append(f'{name}__{step.name}_{fname}.{fending}')

    outputs = sorted(outputs)
    raw = ''.join('>%s   ' % item.ljust(30, ' ') for item in outputs)
    raw = textwrap.fill(raw, 120)
    return raw
