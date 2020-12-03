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
import utila.feature.userinput


def prepare_description(
        name: str,
        description: str,
        workplan: list,
        features: 'utila.feature.collector.FeatureInterfaces',
) -> str:
    """Create help description with in- and outports for program steps.

    Args:
        name(str): application name
        description(str): text which is presented in --help view
        workplan(list): list of WorkingStep's
        features(list): list of feature step documentation
    Returns:
        Prepared description with out- and input-parameter.
    """
    description = description or ''  # convert None to empty
    result = []
    for index, step in enumerate(workplan):
        result.append(f'//{step.name}')
        if features:
            # TODO: REPLACE WITH EMPTY ITER?
            # add step description
            message = features[index].message
            if message:
                message = [f'# {item}' for item in message.splitlines()]
                message = '\n'.join(message)
                result.append(message)
                # result.append('@Parameter:')

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
        if isinstance(source, utila.feature.userinput.Value):
            # for example: <class 'float'>
            datatype = str(source.typ).split("'")[1]
            msg = f'{source.name}({datatype})={source.defaultvar}'
            inputs.append(msg)
        elif isinstance(source, utila.feature.userinput.Bool):
            inputs.append(f'{source.name}(Bool)=True')
        elif isinstance(source, utila.feature.userinput.ResultFile):
            optional = '[?]' if source.optional else ''
            inputs.append(f'{source}{optional}')
        else:
            optional = '[?]' if source.optional else ''
            try:
                fname, fending = source
            except ValueError:
                fname, fending = source, 'yaml'
            inputs.append(f'{fname}.{fending}{optional}')
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
