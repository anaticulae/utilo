# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import contextlib
import copy
import dataclasses
import functools
import glob
import inspect
import os

import utilo
import utilo.cli
import utilo.feature
import utilo.feature.userinput


@dataclasses.dataclass
class ProcessStep:
    name: str = None
    outputs: list = dataclasses.field(default_factory=list)
    hooks: 'utilo.feature.collector.FeatureHooks' = None


ProcessSteps = list[ProcessStep]


def create_runtime(  # pylint:disable=too-many-locals
    plan: list,
    process: str,
    features: 'Features',
    inspace: str,
    outspace: str = None,
    args: dict = None,
    prefix: str = None,
    verify: bool = False,
    used_processes: int = 1,
) -> ProcessSteps:
    """Parse user defined workplan

    Args:
        plan: list of working steps
        process: step name to print on console
        features: list of Features
        inspace(str or list): list of input spaces
        outspace(str): absolute path to write output
        args: dict of additional arguments
        prefix(str): to distinguish different parametrization written in
                     the same folder
        verify(bool): if True, let execution failed on workplan error
        used_processes(int): maximum parallel used processes
    Returns:
        Parsed list of worksteps with verified inputs.
    """
    assert used_processes >= 1, f'invalid process count {used_processes}'
    # if no outspace is defined, use the first passed inspace to write output
    outspace = outspace if outspace else inspace[0]
    prefix = f'{prefix}_' if prefix else ''
    if prefix:
        plan = prefix_workplan(plan, prefix, process)
    hooks = {item.name: item.hooks for item in features}
    args = prepare_args(plan, args)
    result = []
    ret = 0
    for step in plan:
        name = step.name
        utilo.call(f'>> {name}')
        variables = prepare_variables(variables=step.inputs, args=args)
        # optional pages flag is not allowed in workplan
        if utilo.PAGES_FLAG in [item.name for item in step.inputs]:
            utilo.error(str(step.inputs))
            msg = 'parameter `pages` is not allowed in `workplan`, step: %s'
            utilo.error(msg % step.name)
            ret += 1
            continue
        inputs = prepare_inputs(step.inputs, inspace, outspace)
        try:
            caller = hooks[name].work
        except KeyError:
            utilo.error(f'missing hook with name {name}')
            ret += 1
            continue
        outputs = prepare_outputs(
            process=process,
            stepname=name,
            prefix=prefix,
            outputs=step.outputs,
            outspace=outspace,
        )
        ret += verify_resources(inputs)
        stepargs = {
            key: value
            for key, value in args.items()
            if key not in [item.name for item in step.inputs]
        }
        # filter rewrite recursive inputs
        inputs = [item[1:] if item[0] == '_' else item for item in inputs]
        inputs = group_multiple_directories(inputs)
        if variables:
            inputs.extend(variables)
        if args.get(name):
            # shrink verification to selected step
            if verify_interface(
                    inputs,
                    outputs,
                    caller,
                    name,
                    args=stepargs,
            ) == utilo.FAILURE:
                ret += 1
                continue
        function_call = functools.partial(caller, *inputs)
        result.append(
            ProcessStep(
                name=name,
                hooks=utilo.feature.collector.FeatureHooks(
                    work=function_call,
                    before=hooks[name].before,
                    after=hooks[name].after,
                    error=hooks[name].error,
                ),
                outputs=outputs,
            ))
    if ret and verify:
        utilo.exitx()
    return result


def prepare_args(plan, args):
    isall = args.get('all')
    isany = any(args.get(step.name) for step in plan)
    result = dict(args)
    if isall or not isany:
        for step in plan:
            result[step.name] = True
        return result
    return result


def prefix_workplan(
    workplan: 'utilo.WorkPlanSteps',
    prefix: str,
    executor: str,
):
    # TODO: REPLACE COPY WITH OWN CONSTRUCT
    # avoid side effects to other workplans
    workplan = copy.deepcopy(workplan)
    for item in workplan:
        for insignal in item.inputs:
            with contextlib.suppress(AttributeError):
                if insignal.producer == executor:
                    # modify own produced file
                    insignal.name = f'{prefix}{insignal.name}'
    return workplan


def group_multiple_directories(inputs: list) -> list:
    """Merge more than one directory into the first directory bucket."""
    result = []
    multiple_bucket = collections.defaultdict(list)
    for item in inputs:
        counted = count_questionsmarks(item)
        if not counted:
            result.append(item)
            continue
        if not multiple_bucket[counted]:
            # add new multiple bucket
            result.append(multiple_bucket[counted])
        # remove questions marks
        without_questionmarks = item[counted:]
        # insert into correct multiple bucket
        multiple_bucket[counted].append(without_questionmarks)
    return result


def count_questionsmarks(item: str):
    """\
    >>> count_questionsmarks('????C:/datum/info.xml')
    4

    TODO: We do not ignore questions marks in path
    """
    return item.count('?')


def prepare_variables(variables, args):
    """Extract variables out of inputs, ignore files and pattern."""
    result = []
    for variable in variables:
        if isinstance(variable, utilo.Bool):
            if args[variable.name]:
                result.append(True)
            else:
                result.append(False)
            continue
        if not isinstance(variable, utilo.Value):
            continue
        typ = variable.typ
        if typ is None:
            # do not convert data type, just pass it as it is
            typ = utilo.scall_or_me(typ)
        if typ is bool:
            # convert cause every non empty string is converted to true
            typ = utilo.str2bool
        if typ is int:
            typ = utilo.str2int
        try:
            values = args[variable.name]
            defaultvalues = typ(variable.defaultvar)
            converted = typ(values) if values is not None else defaultvalues
            result.append(converted)
        except ValueError:
            utilo.error(f'while process {variable.name} value: {variable.typ}')
            utilo.error(f'given args {args!r}')
    return result


def prepare_inputs(  # pylint:disable=R1260
    inputs: list,
    inspaces: list,
    outspace: str,
) -> list[str]:
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
    utilo.call('prepare inputs')
    result = []
    # single file input
    search_location = ' '.join(inspaces)
    for index, item in enumerate(inputs, start=1):
        lastinput = item == inputs[-1]
        if not isinstance(item, utilo.feature.userinput.Pattern):
            utilo.info(f'skipping input `{item}`, require `Pattern')
            continue
        for inspace in inspaces:
            if isinstance(item, utilo.feature.userinput.ResultFile):
                if prepare_inputs_resultfile(
                        item,
                        inspace,
                        outspace,
                        inspaces,
                        result,
                ):
                    # do not double add path
                    break
                continue
            if isinstance(item, utilo.feature.userinput.File):
                if prepare_inputs_file(
                        item,
                        inspace,
                        search_location,
                        lastinput,
                        result,
                ):
                    # do not double add path
                    break
                continue
            if isinstance(item, utilo.feature.userinput.Directory):
                directory_path = os.path.join(inspace, item.name)
                # Mark `?` to not check existence of folder and group
                # multiple directories which are produced by -i flags to a
                # single entry.
                question_group = '?' * index
                result.append(f'{question_group}{directory_path}')
                continue
            if prepare_inputs_pattern(item, inspace, result):
                # do not double add path
                break
    utilo.call('result:')
    for item in result:
        utilo.call(item)
    return result


def prepare_inputs_resultfile(item, inspace, outspace, inspaces, result):
    filename = str(item)
    filepath = os.path.join(inspace, filename)
    if os.path.exists(filepath):
        result.append(filepath)
        return True
    # TODO: Refactor recursive inputs
    # Only on the last inspace, because the file could exists
    # in other input folder
    if inspace == inspaces[-1]:
        recursivepath = os.path.join(outspace, filename)
        utilo.info(f'recursive input: {recursivepath}')
        result.append(f'_{recursivepath}')
    return False


def prepare_inputs_file(item, inspace, search_location, lastinput, result):
    filename = f'{item.name}.{item.ext}'
    filepath = os.path.join(inspace, filename)
    if os.path.exists(filepath):
        if utilo.isfilepath(filepath):
            # TODO: VERIFY THIS BEHAVIOR
            # ensure that path was not added before. Remove already added
            # file, cause this files exists and must not be genearted.
            fname = utilo.file_name(filepath, ext=True)
            for already in result:
                if utilo.file_name(already, ext=True) == fname:
                    result.remove(already)
                    break
        result.append(filepath)
        # do not double add path
        return True
    if not lastinput:
        return False
    if item.optional:
        result.append(f'_{filepath}')
        return False
    utilo.error(f'search location: {search_location}')
    utilo.error(f'missing input: {filepath}')
    return False


def prepare_inputs_pattern(item, inspace, result):
    name, ext = item.name, item.ext
    _, filename = os.path.split(inspace)
    if '.' in filename and filename[0] != '.':  # .tmp
        # .tmp is not a file name, it is a directory.
        # File as a input name
        result.append(inspace)
        # do not double add path
        return True
    if os.path.isfile(inspace):
        # support dir-like file-path as input
        # TODO: Introduce new datatype?
        result.append(inspace)
        # do not double add path
        return True
    ext = ext.lower()
    pattern = f'{inspace}/{name}.{ext}'
    utilo.info(f'using pattern: {pattern}')
    files = glob.glob(pattern)
    utilo.info(f'{files}')
    for finding in files:
        utilo.info(f'FINDING {finding}')
        result.append(finding)
    return False


def prepare_outputs(
    process: str,
    stepname: str,
    prefix: str,
    outputs: list,
    outspace: str,
) -> list[str]:
    """Support different output types

    Args:
        process(str): name to invoke program by system call
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
                utilo.error(f'check output number {index}!')
                msg = ('require tuple with (item, datatype).'
                       f' got: {item!r} {type(item)}')
                utilo.error(msg)
                ret += 1
        if isinstance(item, utilo.File):  # pylint:disable=W0160
            outitem = f'{filename}.{datatype}'
        else:
            outitem = f'{process}__{prefix}{stepname}_{filename}.{datatype}'
        _outputs.append(outitem)
    if ret:
        utilo.exitx()
    outputs = [os.path.join(outspace, item) for item in _outputs]
    return outputs


def verify_resources(inputs):
    ret = 0
    # require input files
    for path in inputs:
        if os.path.exists(path):
            continue
        if path[0] in {'_', '?'}:
            # recursive input-definition start with _. We do not check
            # recursive inputs, because there will be generated later.
            continue
        utilo.error(f'File does not exists: {path}')
        ret += 1
    return ret


MAGICS = 'inputs outputs prefix pipeline'.split()


def verify_interface(inputs, outputs, worker, stepname, args: dict = None):
    if args is None:
        args = {}
    # check callable
    # check input parameter
    call_parameter = inspect.signature(worker).parameters
    parameter = [str(item) for item in call_parameter.values()]
    # variable name of input parameter
    dynamic_collection = len([item for item in parameter if '*' in item]) == 1
    if not dynamic_collection:
        # Optional pages flag, reduces count of required parameter in
        # definition.
        magics = [
            item for item in call_parameter
            if item in MAGICS or (item in args and item not in parameter)
        ]
        has_pages = int(utilo.PAGES_FLAG in call_parameter)
        required_callparameter = len(inputs) + has_pages + len(magics)
        if len(call_parameter) != required_callparameter:
            utilo.error('interface error: missing input resources\n'
                        f'step: {stepname}\n'
                        f'expected: {list(call_parameter.keys())}\n'
                        f'got: {inputs}\n'
                        f'magics: {magics}')
            return utilo.FAILURE
    # check output parameter
    return_parameter = str(inspect.signature(worker).return_annotation)
    supported = ('str', 'bytes')
    return_count = sum((return_parameter.count(typ) for typ in supported))
    variable_returnvalues = utilo.feature.outpath.variable_parameter(outputs)
    if not len(outputs) == return_count and not variable_returnvalues:
        utilo.error(f'missing output resources: '
                    f'interface error {return_parameter} != {outputs}')
        return utilo.FAILURE
    return utilo.SUCCESS


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


# @utilo.refactor(major=3, description='extend documentation')
def input_order(plan, root):
    require = collections.defaultdict(set)
    for step in plan:
        name = f'{root}{REQUIREMENT_SEPARATOR}{step.name}'
        if isinstance(step, utilo.WorkPlanStep):  # pylint:disable=W0160
            items = step.inputs
        else:
            items = step.hooks.work.args
        inputs = remove_common_path(items)
        if not inputs:
            # no required input - for example a random number generator
            # without using a seed :).
            _ = require[name]  # create empty set
        for item in inputs:
            try:
                fname = input_name(item)
                require[name].add(fname)
            except ValueError:
                # for example input.pdf
                require[name].add(item)
    order = utilo.utils.determine_order(
        require,
        flats=False,
    )
    return order


def remove_common_path(inputs):
    r"""Remove common path, which is equal for every input but
    destroy the required file analysis in `determine_order`.

    >>> remove_common_path(['C:\\restruct\\rawmaker__text_positions.yaml',
    ... 'C:\\restruct\\groupme__pagenumbers_pagenumbers.yaml'])
    ['rawmaker__text_positions.yaml', 'groupme__pagenumbers_pagenumbers.yaml']

    Cleanup has single folder as input
    >>> remove_common_path(('',))
    []
    """
    inputs = [str(item) for item in inputs if item]  # remove empty item
    inputs = [utilo.file_name(item, ext=True) for item in inputs]
    return inputs


def input_name(item: str) -> str:
    """\
    >>> input_name('rawmaker__text_positions.yaml')
    'rawmaker:text'
    """
    item = item.replace('.yaml', '')
    producer, filename = item.split('__', maxsplit=1)
    # TODO: THINK ABOUT EXTETERNAL FILE WHICH CONTAINS DUNDER _
    if '_' in filename:
        if filename.count('_') == 2:
            # with prefix
            _, step, __ = filename.split('_', maxsplit=2)
        else:
            # without prefix
            step, _ = filename.split('_', maxsplit=1)
    else:
        step = filename
    result = f'{producer}{REQUIREMENT_SEPARATOR}{step}'
    return result
