# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""How to use a featurepack

    completed = featurepack(
        WORKPLAN,
        FEATURE_PATH,
        PROCESS_NAME,
        PROCESS_DESCRIPTION,
        VERSION,
    )
"""
import collections
import concurrent.futures
import contextlib
import dataclasses
import functools
import glob
import importlib
import inspect
import os
import typing

import utila
from utila.cli import PAGES_FLAG
from utila.cli import Command
from utila.cli import Flag
from utila.cli import Parameter
from utila.cli import create_parser
from utila.cli import evaluate_flags
from utila.cli import parse
from utila.cli import sources
from utila.cli import userflag_to_arg
from utila.error import saveme
from utila.file import file_replace
from utila.logger import Level
from utila.logger import call
from utila.logger import error
from utila.logger import info
from utila.logger import level_setup
from utila.logger import log
from utila.logger import log_stacktrace
from utila.utils import FAILURE
from utila.utils import NEWLINE
from utila.utils import SUCCESS
from utila.utils import determine_order

FeatureInterface = typing.Tuple[str, Command, callable]

WorkStep = collections.namedtuple('WorkStep', 'name inputs outputs')

ErrorHook = typing.Tuple[str, Exception]


class InterfaceMismatch(TypeError):
    pass


@saveme(systemexit=True)
def featurepack(
        workplan: typing.List[WorkStep],
        root: str,
        description: str,
        featurepackage: str,
        name: str,
        version: str,
        errorhook: ErrorHook = None,
        *,
        failfastflag: bool = True,
        flags: list = None,
        multiprocessed: bool = False,
        pages: bool = False,
        singleinput: bool = False,
        verboseflag: bool = True,

) -> int:
    """Run featurepack defined in `workplan`

    Args:
        workplan:
        root(str): path to project root
        featurepackage(str): location to featurepackage releative to root
        name(str): name to invoke cmdline tool
        description(str): description shown in cmdline tool
        version(str): version to display with --version command
        singleinput(bool): if true, files as input are allowed, else only
                           directories are allowed
    Returns:
        return SUCCESS or FAILURE
    """
    flags = flags if flags else []
    feature = find_features(root, featurepackage)
    commands = commandline(feature, workplan)

    description = prepare_description(name, description, workplan)
    parser = create_parser(
        commands,
        description=description,
        failfastflag=failfastflag,
        flags=flags,
        inputparameter=True,
        multiprocessed=multiprocessed,
        outputparameter=True,
        pages=pages,
        prog=name,
        verboseflag=verboseflag,
        version=version,
    )
    args = parse(parser)

    processes, failfast, pages = evaluate_flags(args, multiprocessed)
    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = sources(
        args,
        singleinput=singleinput,
        verbose=True,
    )

    # update logging level
    level_setup(Level(verbose))

    hooks = prepare_hooks(feature)
    workplan = read_workplan(
        workplan,
        process_=name,
        hooks=hooks,
        inspace=inputpath,
        outspace=outputpath,
        args=args,
        prefix=prefix,
        used_processes=processes,
        verify=True,
    )
    # an empty workplan is defined by user code, feature pack does nothing
    if not workplan:
        error('empty workplan - nothing todo - abort!')
        exit(FAILURE)

    # Ensure to have output folder
    os.makedirs(outputpath, exist_ok=True)

    current_todo = determine_todo(args, flags)
    completed = process(
        workplan,
        name,
        errorhook=errorhook,
        failfast=failfast,
        pages=pages,
        processes=processes,
        todo=current_todo,
    )
    return completed


def process(
        workplan: typing.List[WorkStep],
        name: str = None,
        todo: typing.List = None,
        processes: int = 1,
        pages: list = None,
        errorhook: ErrorHook = None,
        *,
        failfast: bool = False,
):
    """Process the given features. The process ignores errors in
    sub-steps and run till the end. If some error occurs, the process
    returns an `FAILURE` after finishing. If the todo-list is empty,
    every single step is processed.

    Args:
        workplan(List[WorkStep]):
        name(str): name of executable
        todo: list with steps to run, if no steps are None, every step is
              executed
        processes(int): maximal parallel exection steps
        pagenumbers(list): list with processed pages
        failfast(bool): quit after first failure
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    todo = prepare_process(todo, name, processes)

    workplan = parallelize_workplan(
        workplan,
        root=name,
        max_processes=processes,
    )

    executor = select_executor()
    with executor(max_workers=processes) as pool:
        failure = 0
        for level in workplan:
            # wait that level finishes without waiting, a next level which
            # require resource of the current may will not find the
            # resource, cause the excution is not done.
            results = run_level(level, todo, pool, name, pages)

            # write result
            failure += write_level_result(
                results,
                errorhook=errorhook,
                failfast=failfast,
            )
            if failfast and failure:
                return FAILURE
    status = utila.FAILURE if failure else utila.SUCCESS
    return status


def run_level(level, todo, pool, runnable, pages):
    results = []
    for step in level:
        # if todo is empty, nothing is selected, run every step
        if step.name not in todo and todo:
            log(f'skipping: {step.name}')
            continue
        future = pool.submit(
            callback,
            step.inputs,
            stepname=step.name,
            output=step.outputs,
            pages=pages,
        )
        results.append(future)

    return results


def write_level_result(
        results,
        errorhook: ErrorHook = None,
        *,
        failfast=False,
) -> int:
    success = True
    for result in results:
        completed = result.result()
        result, name, _ = completed
        if isinstance(result, Exception):
            if errorhook:
                errorhook(result, name)
            success = False
            if failfast:
                return FAILURE
        else:
            written = write_result_safely(*completed)
            if written == FAILURE:
                success = False
                if failfast:
                    return FAILURE
    return utila.SUCCESS if success else utila.FAILURE


def callback(hook, stepname: str, output, pages: list):
    """
    Args:
        hook:
        stepname(str): name of working step
        output(str): path to write step output
        pages(list): list with pages to processed
    """
    log(f'processing: {stepname}')
    # run runnable
    runnable = functools.partial(
        run_hook_safely,
        hook=hook,
        name=stepname,
        stepoutput=output,
        pages=pages,
    )
    try:
        result = runnable()
        log(f'completed: {stepname}')
    except Exception as exception:  # pylint:disable=broad-except
        error(f'failed: {stepname}')
        result = exception
    return [result, stepname, output]


def run_hook_safely(
        hook: callable,
        name: str,
        stepoutput,
        pages,
) -> int:
    sig = inspect.signature(hook)
    try:
        if PAGES_FLAG in sig.parameters:
            # optional page numbers flag
            result = hook(pages=pages)
        else:
            result = hook()
    except Exception as msg:  # pylint: disable=broad-except
        log_stacktrace()
        error('while processing %s' % name)
        error(msg)
        raise

    if isinstance(result, str):
        result = [result]
    # Verify result
    if result and len(stepoutput) != len(result):
        error('wrong return value count')
        error('interface count %d' % len(stepoutput))
        error('return count from method %d' % len(result))
        raise InterfaceMismatch
    return result


def write_result_safely(result, processstep, outputstep):
    call('write results')
    try:
        for path, content in zip(outputstep, result):
            info('write %s' % path)
            # write content to file.
            file_replace(path, content)
        return SUCCESS
    except TypeError as msg:
        error('while processing %s' % processstep)
        error('wrong return value')
        error('current return value: %s' % result)
        error(msg)
        return FAILURE


def select_executor():
    # TODO: how to use multiprocessing with pytest, see pytest: 38.3.1
    testrun = os.environ.get('PYTEST_PLUGINS', False)
    executor = concurrent.futures.ProcessPoolExecutor
    if testrun:
        executor = concurrent.futures.ThreadPoolExecutor
    return executor


def prepare_process(todo, name, processes):
    if todo is None:
        todo = []
    todo = set(todo)
    # process all features, see some lines below
    if 'all' in todo:
        todo = set()
    if name:
        # log start of executable
        log(name)
    if processes > 1:
        log('use multiple processes')
    return todo


def prepare_hooks(items: typing.List[FeatureInterface]):
    result = {}
    for item in items:
        name, _, caller = item
        result[name] = caller
    return result


def prepare_description(name: str, description: str, workplan):
    result = [
        '\nworking plan resources:\n',
    ]
    for item in workplan:
        result.append('step:\n   %s' % item.name)

        # prepare inputs
        result.append('inputs:')
        inputs = []
        for input_ in item.inputs:
            if isinstance(input_, Value):
                msg = '   variable: %s, type: %s, default: %s'
                msg = msg % (input_.name, input_.typ, str(input_.defaultvar))
                inputs.append(msg)
            else:
                try:
                    fname, fending = input_
                except ValueError:
                    fname, fending = input_, 'yaml'
                inputs.append('   %s.%s' % (fname, fending))
        result.extend(sorted(inputs))

        # prepare outputs
        result.append('outputs:')
        outputs = []
        for output_ in item.outputs:
            try:
                fname, fending = output_
            except ValueError:
                fname, fending = output_, 'yaml'
            outputs.append('   %s__%s.%s' % (name, fname, fending))
        result.extend(sorted(outputs))

        # final newline
        result.append('')
    result = NEWLINE.join(result)
    return description + NEWLINE + result


def find_features(
        root: str,
        featurepackage: str,
) -> typing.List[FeatureInterface]:
    """Locate all feautures in given path

    Ensure that feature methods are defined. If some feature interface is not
    implemented properly, the exection ends with FAILURE.
    """
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
    assert os.path.exists(root), root
    if not os.path.exists(featurepath):
        error('wrong featurepack configuration, check `featurepackage` path')
        error('featurepath %s does not exists' % featurepath)
        exit(FAILURE)
    collected = [
        item.replace('.py', '')
        for item in os.listdir(featurepath)
        if not '__init__' in item and item.endswith('.py')
    ]
    result = []
    ret = 0
    for item in collected:
        current = importlib.import_module(
            featurepackage + '.' + item,
            featurepackage,
        )
        try:
            result.append(connect_feature_interface(current, item))
        except AttributeError as exception:
            error('SKIP LOADING %s' % item)
            error(exception)
            ret += 1
    if ret:
        exit(FAILURE)
    return result


def connect_feature_interface(current, item) -> FeatureInterface:
    """Ensure that feature supports `name`, `commandline` and `work`-method"""
    curname = current.name() if hasattr(current, 'name') else item

    # no commandline information is defined
    def curcommandline():
        return Flag(longcut=curname, message='export %s' % curname)

    if hasattr(current, 'commandline'):
        curcommandline = current.commandline

    return (curname, curcommandline, current.work)


Name = str
CommandLineInterface = typing.List[Command]
Worker = callable  #pylint:disable=C0103
Feature = typing.Tuple[Name, CommandLineInterface, Worker]


def commandline(
        features: typing.List[Feature],
        workplan,
) -> typing.List[Command]:
    """Build command line interface due iterating searched features

    Args:
        features: list of parsed features
    Returns:
        list of `Command`s
    """
    result = []
    # name, cmd, work
    for _, command, _ in features:
        commands = command()
        # one single command is iterable, testing of Iterable is not possible
        if isinstance(commands, (list, tuple)):
            # support adding commands from iterable and single command
            result.extend(commands)
        else:
            result.append(commands)
    # add sorted, unique parameter as parameterization point
    variables = determine_variables(workplan)
    variables = list(set(variables))  # avoid duplicating parameter
    for item in sorted(variables):
        result.append(Parameter(longcut=item))

    # run all workplan feature
    result.append(Flag(longcut='all'))

    return result


def create_step(
        name: str,
        inputs: typing.List['Input'],
        output: typing.Tuple[str],
):
    """
    step = {
        NAME: name,
        INPUT: [
            ('groupme', 'chapter'),
            ('iamraw', 'toc'),
        ],
        OUTPUT: ('butter', 'tart', 'cream'),
    }
    """
    assert isinstance(inputs, list), '%s %s' % (type(inputs), str(inputs))
    for index, item in enumerate(inputs):
        assert isinstance(item, Input), f'{index} {item}'
    assert isinstance(output, tuple), '%s %s' % (type(output), str(output))
    return WorkStep(name, inputs, output)


def read_workplan(
        plan,
        process_: str,
        hooks: dict,
        inspace,
        outspace=None,
        args=None,
        prefix: str = None,
        verify: bool = False,
        used_processes: int = 1,
) -> typing.List[WorkStep]:
    """Parse user defined workplan

    Args:
        plan:
        process_: step name to print on console
        hooks:
        inspace([str]): list of input spaces
        outspace(str): absolute path to write output
        args:
        prefix(str): to distingush different parameterization written in the
                     same folder
        verify(bool): if True, let execution failed on workplan error
        processes(int): maximum parallel used processes
    Returns:
        parsed list of worksteps with verified inputs
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
        if PAGES_FLAG in [item.name for item in step.inputs]:
            error(str(step.inputs))
            msg = 'parameter `pages` is not allowed in `workplan`, step: %s'
            error(msg % step.name)
            ret += 1
            continue

        call_inputs = prepare_inputs(step.inputs, inspace, outspace)
        name = step.name
        try:
            caller = hooks[name]
        except KeyError:
            error('missing hook with name %s' % name)
            ret += 1
            continue

        outputs = prepare_outputs(
            process_=process_,
            stepname=name,
            prefix=prefix,
            outputs=step.outputs,
            outspace=outspace,
        )
        ret += verify_resources(call_inputs)
        # filter rewrite recursive inputs
        call_inputs = [
            item[1:] if item[0] == '_' else item for item in call_inputs
        ]
        if variables:
            call_inputs.extend(variables)
        if verify_interface(call_inputs, outputs, caller) == FAILURE:
            ret += 1
            continue
        function_call = functools.partial(caller, *call_inputs)

        result.append(WorkStep(name, function_call, outputs))

    if ret and verify:
        exit(FAILURE)
    return result


def parallelize_workplan(
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
    order = determine_order(require, flat=False)
    return order


def determine_variables(workplan):
    result = []
    for step in workplan:
        for item in step.inputs:
            if not isinstance(item, Value):
                continue
            result.append(item.name)
    return result


def prepare_variables(variables, args):
    """Extract variables out of inputs, ignore files and pattern"""
    result = []
    for variable in variables:
        if not isinstance(variable, Value):
            continue
        typ = variable.typ
        try:
            values = args[variable.name]
            defaultvalues = typ(variable.defaultvar)
            converted = typ(values) if values is not None else defaultvalues
            result.append(converted)
        except ValueError:
            msg = 'while processing %s with value %s'
            error(msg % (variable.name, variable.typ))
            error('given args %r' % args)
    return result


def prepare_inputs(inputs, inspaces, outspace) -> typing.List[str]:
    """Parse single and multiple file input

    Loacted files by defined pattern in `Workplan`. A file pattern is defined
    via (name, typ). The ext is in UPPER-CASES, for example (*, PDF) to
    locate multiple pdf's.

    Args:
        inputs(str): inputs is deliverd by workplan
        inspaces([str]): inspaces is the current input via -i
    Returns:
        list of located files
    """

    call('prepare inputs')
    result = []
    # single file input
    search_location = ' '.join(inspaces)
    for item in inputs:
        lastinput = item == inputs[-1]
        info('skipping input `%s`, require `Pattern' % str(item))
        if not isinstance(item, Pattern):
            continue
        (name, ext) = item.name, item.ext
        for inspace in inspaces:
            if isinstance(item, ResultFile):
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
                        info('recursive input %s' % recursivepath)
                        result.append('_%s' % recursivepath)
            elif isinstance(item, File):
                filename = '%s.%s' % (name, ext)
                filepath = os.path.join(inspace, filename)
                if os.path.exists(filepath):
                    result.append(filepath)
                    break  # do not double add path
                else:
                    if not lastinput:
                        continue
                    error('search location: %s' % search_location)
                    error('missing input: %s' % filepath)
            else:
                _, filename = os.path.split(inspace)
                if '.' in filename:
                    # File as a input name
                    result.append(inspace)
                    break  # do not double add path
                else:
                    ext = ext.lower()
                    pattern = '%s/%s.%s' % (inspace, name, ext)
                    info('using pattern: %s' % pattern)
                    files = glob.glob(pattern)
                    info('%s' % str(files))
                    for finding in files:
                        log('FINDING %s' % finding)
                        result.append(finding)

    call('result: %s\n' % result)
    return result


def prepare_outputs(
        process_: str,
        stepname: str,
        prefix: str,
        outputs: str,
        outspace: str,
) -> typing.List[str]:
    """Support different output types

    Args:
        process(str):
        prefix(str): optional to add prefix to differentiate output files
        outputs(str):
        outspace(str): folder to write results
    Returns:
        a list with paths to write output
    """
    ret = 0
    _outputs = []
    for index, item in enumerate(outputs):
        datatype = 'yaml'
        if not isinstance(item, str):
            try:
                item, datatype = item
            except ValueError:
                error('checking output number %d' % index)
                msg = 'require tuple with (item, datatype). got: %r %s'
                error(msg % (item, type(item)))
                ret += 1
        outitem = '%s__%s%s_%s.%s'
        outitem = outitem % (process_, prefix, stepname, item, datatype)
        _outputs.append(outitem)

    if ret:
        exit(FAILURE)
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
            # recursive inputs, because there were generated later.
            continue
        error('File does not exists: %s' % path)
        ret += 1
    return ret


def verify_interface(inputs, outputs, worker):
    # check callable
    # check input parameter
    call_parameter = inspect.signature(worker).parameters
    interface_error_msg = 'interface error %s != %s' % (
        list(call_parameter.keys()),
        inputs,
    )

    # optional pages flag, reduces count of required parameter in definition
    has_pages = int(PAGES_FLAG in call_parameter)
    if not len(call_parameter) == len(inputs) + has_pages:
        error('missing input resources: %s' % interface_error_msg)
        return FAILURE

    # check output parameter
    return_parameter = str(inspect.signature(worker).return_annotation)
    return_count = return_parameter.count('str')
    interface_error_msg = 'interface error %s != %s' % (
        return_parameter,
        outputs,
    )
    if not len(outputs) == return_count:
        error('missing output resources: %s' % interface_error_msg)
        return FAILURE
    return SUCCESS


def determine_todo(args: dict, flags: list) -> typing.List[str]:
    """Remove flags from feature todo list

    Hint:
        See feature selection approach.

    Args:
        args(dict): user defined command line arguments
        flags(tuple/str): possible bool flag args for examle `--linter`
    Returns:
        args list without possible flag-args
    """
    args = dict(args)
    del args['input']
    del args['output']

    def remove_bool_flags(cli_args, flags):
        # We have to remove all flags, which are not possible to do flags.
        # The to do mechanism run all features if no to do flag is passed.
        # If one flag is left, which is not releated to todo flag like
        # `--linter_writing` every todo-job is skipped, therefore we have
        # to remove all external flags.
        for item in flags:
            try:
                flag, _ = item
            except ValueError:
                flag = item
            flag = userflag_to_arg(flag)
            with contextlib.suppress(KeyError):
                # remove present user flags.
                del cli_args[flag]
        return cli_args

    args = remove_bool_flags(args, flags)

    if not any(args.values()):
        # run all features
        result = [key for key in args.keys()]
    else:
        # True is important!
        result = [key for key, value in args.items() if value == True]  # pylint:disable=singleton-comparison
    return result


@dataclasses.dataclass  # pylint:disable=R0903
class Input:
    pass


@dataclasses.dataclass  # pylint:disable=R0903
class Value(Input):
    name: str
    typ: str
    defaultvar: str
    minimum: str = ''
    maximum: str = ''

    def __repr__(self):
        ctor = ("Value(name='%s', typ='%s', defaultvar='%s',"
                " minimum='%s', maximum='%s',)")
        return ctor % (
            self.name,
            self.typ,
            self.defaultvar,
            self.minimum,
            self.maximum,
        )


@dataclasses.dataclass
class Pattern(Input):
    name: str
    ext: str

    def __str__(self):
        return '%s.%s' % (self.name, self.ext)

    def __getitem__(self, index):
        # make pattern iterable
        return [self.name, self.ext][index]


@dataclasses.dataclass  # pylint:disable=R0903
class File(Pattern):
    ext: str = 'yaml'


@dataclasses.dataclass  # pylint:disable=R0903
class ResultFile(File):
    producer: str = 'default'

    def __init__(self, producer: str, name: str):
        self.producer = producer
        self.name = name

    def __str__(self):
        return '%s__%s.%s' % (self.producer, self.name, self.ext)
