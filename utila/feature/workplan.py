# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import functools
import glob
import inspect
import os
import typing

import utila
import utila.cli
import utila.feature
import utila.feature.userinput


def read_workplan(  # pylint:disable=too-many-locals
        plan: list,
        process_: str,
        hooks: dict,
        inspace: str,
        outspace: str = None,
        args: dict = None,
        prefix: str = None,
        verify: bool = False,
        used_processes: int = 1,
) -> 'typing.List[WorkStep]':
    """Parse user defined workplan

    Args:
        plan: list of working steps
        process_: step name to print on console
        hooks: dict of name and callable function
        inspace(str or list): list of input spaces
        outspace(str): absolute path to write output
        args: dict of additonal arguments
        prefix(str): to distingush different parameterization written in the
                     same folder
        verify(bool): if True, let execution failed on workplan error
        used_processes(int): maximum parallel used processes
    Returns:
        Parsed list of worksteps with verified inputs.
    """
    assert used_processes >= 1, 'invalid process count %d' % used_processes
    # if no outspace is defined, use the first passed inspace to write output
    outspace = outspace if outspace else inspace[0]
    prefix = '%s_' % prefix if prefix else ''

    result = []
    ret = 0
    for step in plan:
        variables = prepare_variables(variables=step.inputs, args=args)
        # optional pages flag is not allowed in workplan
        if utila.PAGES_FLAG in [item.name for item in step.inputs]:
            utila.error(str(step.inputs))
            msg = 'parameter `pages` is not allowed in `workplan`, step: %s'
            utila.error(msg % step.name)
            ret += 1
            continue

        inputs = prepare_inputs(step.inputs, inspace, outspace)
        name = step.name
        try:
            caller = hooks[name]
        except KeyError:
            utila.error('missing hook with name %s' % name)
            ret += 1
            continue

        outputs = prepare_outputs(
            process_=process_,
            stepname=name,
            prefix=prefix,
            outputs=step.outputs,
            outspace=outspace,
        )
        ret += verify_resources(inputs)
        # filter rewrite recursive inputs
        inputs = [item[1:] if item[0] == '_' else item for item in inputs]
        if variables:
            inputs.extend(variables)
        if verify_interface(inputs, outputs, caller, name) == utila.FAILURE:
            ret += 1
            continue
        function_call = functools.partial(caller, *inputs)

        result.append(utila.feature.WorkStep(name, function_call, outputs))

    if ret and verify:
        exit(utila.FAILURE)
    return result


def prepare_variables(variables, args):
    """Extract variables out of inputs, ignore files and pattern."""
    result = []
    for variable in variables:
        if isinstance(variable, utila.Bool):
            if args[variable.name]:
                result.append(True)
            else:
                result.append(False)
            continue
        if not isinstance(variable, utila.Value):
            continue
        typ = variable.typ
        if typ is bool:
            # convert cause every non empty string is converted to true
            typ = utila.utils.str2bool
        if typ is int:
            typ = utila.utils.str2int
        try:
            values = args[variable.name]
            defaultvalues = typ(variable.defaultvar)
            converted = typ(values) if values is not None else defaultvalues
            result.append(converted)
        except ValueError:
            msg = 'while processing %s with value %s'
            utila.error(msg % (variable.name, variable.typ))
            utila.error('given args %r' % args)
    return result


def prepare_inputs(  # pylint:disable=too-many-locals,too-complex,too-many-branches,too-many-statements
        inputs: list,
        inspaces: list,
        outspace: str,
) -> typing.List[str]:
    """Parse single and multiple file input

    Locate files by defined pattern in `Workplan`. A file pattern is
    defined via (name, typ). The ext is in UPPER-CASES, for example (*,
    PDF) to locate multiple pdf's.

    Args:
        inputs(str): inputs are defined in a workplan
        inspaces(str): inspaces is the current input via -i
        outspace(str): path to write results and use as possible input
                       source for `recursive inputs`.
    Returns:
        List of located files.
    """

    utila.call('prepare inputs')
    result = []
    # single file input
    search_location = ' '.join(inspaces)
    for item in inputs:
        lastinput = item == inputs[-1]
        utila.info('skipping input `%s`, require `Pattern' % str(item))
        if not isinstance(item, utila.feature.userinput.Pattern):
            continue
        (name, ext) = item.name, item.ext
        for inspace in inspaces:
            if isinstance(item, utila.feature.userinput.ResultFile):
                producer = item.producer
                filename = '%s__%s.%s' % (producer, name, ext)
                filepath = os.path.join(inspace, filename)
                if os.path.exists(filepath):
                    result.append(filepath)
                    break  # do not double add path
                else:
                    # TODO: Refactor recursive inputs
                    # Only on the last inspace, because the file could exists
                    # in other input folder
                    if inspace == inspaces[-1]:
                        recursivepath = os.path.join(outspace, filename)
                        utila.info('recursive input %s' % recursivepath)
                        result.append('_%s' % recursivepath)
            elif isinstance(item, utila.feature.userinput.File):
                filename = '%s.%s' % (name, ext)
                filepath = os.path.join(inspace, filename)
                if os.path.exists(filepath):
                    result.append(filepath)
                    break  # do not double add path
                else:
                    if not lastinput:
                        continue
                    utila.error('search location: %s' % search_location)
                    utila.error('missing input: %s' % filepath)
            elif isinstance(item, utila.feature.userinput.Directory):
                directory_path = os.path.join(inspace, name)
                # mark `_` to not check existence of folder
                result.append(f'_{directory_path}')
            else:
                _, filename = os.path.split(inspace)
                if '.' in filename and filename[0] != '.':  # .tmp
                    # .tmp is not a file name, it is a directory.
                    # File as a input name
                    result.append(inspace)
                    break  # do not double add path
                elif os.path.isfile(inspace):
                    # support dir-like file-path as input
                    # TODO: Introduce new datatype?
                    result.append(inspace)
                    break  # do not double add path
                else:
                    ext = ext.lower()
                    pattern = '%s/%s.%s' % (inspace, name, ext)
                    utila.info('using pattern: %s' % pattern)
                    files = glob.glob(pattern)
                    utila.info('%s' % str(files))
                    for finding in files:
                        utila.info('FINDING %s' % finding)
                        result.append(finding)
    utila.call(f'result: {result}')
    return result


def prepare_outputs(
        process_: str,
        stepname: str,
        prefix: str,
        outputs: list,
        outspace: str,
) -> typing.List[str]:
    """Support different output types

    Args:
        process_(str): name to invoke program by system call
        stepname(str): a step describes a part of working in the process
        prefix(str): optional to add prefix to differentiate output files
        outputs(list): list of items to write results of steps as files
        outspace(str): folder to write results
    Returns:
        a list with paths to write output
    """
    ret = 0
    _outputs = []
    for index, item in enumerate(outputs):
        filename = item
        datatype = 'yaml'
        if not isinstance(item, str):
            try:
                filename, datatype = item
            except TypeError:
                utila.error(f'check output number {index}!')
                msg = ('require tuple with (item, datatype).'
                       f' got: {item!r} {type(item)}')
                utila.error(msg)
                ret += 1
        if isinstance(item, utila.File):
            outitem = f'{filename}.{datatype}'
        else:
            outitem = f'{process_}__{prefix}{stepname}_{filename}.{datatype}'
        _outputs.append(outitem)
    if ret:
        exit(utila.FAILURE)
    outputs = [os.path.join(outspace, item) for item in _outputs]
    return outputs


def verify_resources(inputs):
    ret = 0
    # require input files
    for path in inputs:
        if os.path.exists(path):
            continue
        if path[0] == '_':
            # recursive input-definition start with _. We do not check
            # recursive inputs, because there will be generated later.
            continue
        utila.error('File does not exists: %s' % path)
        ret += 1
    return ret


def verify_interface(inputs, outputs, worker, stepname):
    # check callable
    # check input parameter
    call_parameter = inspect.signature(worker).parameters
    parameter = [str(item) for item in call_parameter.values()]
    # variable name of input parameter
    dynamic_collection = len([item for item in parameter if '*' in item]) == 1
    if not dynamic_collection:
        # Optional pages flag, reduces count of required parameter in
        # definition.
        has_pages = int(utila.PAGES_FLAG in call_parameter)
        required_callparameter = len(inputs) + has_pages
        if len(call_parameter) != required_callparameter:
            utila.error('interface error: missing input resources\n'
                        f'step: {stepname}\n'
                        f'expected: {list(call_parameter.keys())}\n'
                        f'got: {inputs}')
            return utila.FAILURE

    # check output parameter
    return_parameter = str(inspect.signature(worker).return_annotation)
    supported = ('str', 'bytes')
    return_count = sum([return_parameter.count(typ) for typ in supported])

    variable_returnvalues = utila.feature.variable_parameter(outputs)
    if not len(outputs) == return_count and not variable_returnvalues:
        utila.error(f'missing output resources: '
                    f'interface error {return_parameter} != {outputs}')
        return utila.FAILURE
    return utila.SUCCESS


def parallelize(
        plan,
        root,
        *,
        max_processes=1,
):
    order = input_order(plan, root)
    steps = {f'{root}{REQUIREMENT_SEPARATOR}{step.name}': step for step in plan}
    result = []
    for level in order:
        level_result = []
        for item in level:
            if len(level_result) < max_processes:
                level_result.append(steps[item])
            else:
                result.append(level_result)
                level_result = [steps[item]]
        if level_result:
            result.append(level_result)
    return result


REQUIREMENT_SEPARATOR = ':'


@utila.refactor(major=2, description='extend documentation')
def input_order(plan, root):
    require = collections.defaultdict(set)
    for step in plan:
        name = f'{root}{REQUIREMENT_SEPARATOR}{step.name}'
        try:
            # TODO: ADD MORE DOCS HERE
            # determine args out of  partial.method?
            inputs = [str(item) for item in step.inputs.args]
        except AttributeError:
            inputs = [str(item) for item in step.inputs]

        def remove_common_path(inputs):
            """Remove common path, which is equal for every inputs but
            destroy the required file analysis in `determine_order`.

            'C:\\restruct\\rawmaker__text_positions.yaml',
            'C:\\restruct\\groupme__pagenumbers_pagenumbers.yaml'

            'rawmaker__text_positions.yaml',
            'groupme__pagenumbers_pagenumbers.yaml'
            """
            inputs = [os.path.split(item)[1] for item in inputs]
            return inputs

        inputs = remove_common_path(inputs)
        if not inputs:
            # no required input - for example a random number generator
            # without using a seed :).
            _ = require[name]  # create empty set
        for item in inputs:
            try:
                item = item.replace('.yaml', '')
                producer, file_ = item.split('__', maxsplit=1)
                if '_' in file_:
                    step, _ = file_.split('_', maxsplit=1)
                else:
                    step = file_
                require[name].add(f'{producer}{REQUIREMENT_SEPARATOR}{step}')
            except ValueError:
                # for example input.pdf
                require[name].add(item)
    order = utila.utils.determine_order(require, flat=False)
    return order
