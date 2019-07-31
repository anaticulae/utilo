# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""How to use a featurepack:

    completed = featurepack(
        WORKPLAN,
        FEATURE_PATH,
        PROCESS_NAME,
        PROCESS_DESCRIPTION,
        VERSION,
    )
"""
import importlib
import os
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from glob import glob
from inspect import signature
# pylint:disable=ungrouped-imports
from os import listdir
from os import makedirs
from os.path import exists
from os.path import join
from os.path import split
from typing import Callable
from typing import List
from typing import Tuple

from utila.cmdline import Command
from utila.cmdline import Flag
from utila.cmdline import Parameter
from utila.cmdline import create_parser
from utila.cmdline import parse
from utila.cmdline import sources
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

NAME = 'name'
INPUT = 'input'
OUTPUT = 'output'
HOOK = 'hook'

FeatureInterface = Tuple[str, Command, callable]

Outputs = List[str]
Hook = Callable
Name = str
WorkStep = Tuple[Name, Hook, Outputs]


@saveme(systemexit=True)
def featurepack(
        workplan: List[WorkStep],
        root: str,
        featurepackage: str,
        name: str,
        description: str,
        version: str,
        *,
        multiprocessed: bool = False,
        singleinput: bool = False,
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
    feature = find_features(root, featurepackage)
    commands = commandline(feature, workplan)

    description = prepare_description(name, description, workplan)
    parser = create_parser(
        commands,
        prog=name,
        description=description,
        version=version,
        inputparameter=True,
        multiprocessed=multiprocessed,
        outputparameter=True,
    )
    args = parse(parser)

    processes = 1 if not multiprocessed else args.get('processes')
    if multiprocessed:
        del args['processes']

    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = sources(
        args,
        singleinput=singleinput,
        verbose=True,
    )

    # update logging level
    level_setup(Level(verbose))

    # run application in current working directory if not paths are provided
    if not inputpath:
        inputpath = [os.getcwd()]
    if not outputpath:
        outputpath = os.getcwd()

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
    makedirs(outputpath, exist_ok=True)

    current_todo = determine_todo(args)
    completed = process(
        workplan,
        name,
        todo=current_todo,
    )
    return completed


def process(
        workplan: List[WorkStep],
        name: str = None,
        todo: List = None,
        processes: int = 1,
):
    """Process the given features. The process ignores errors in sub-steps
    and run till the end. If some error occurs, the process stoppes at the
    end. If the todo-list is empty, every single step is executed.

    Args:
        workplan(List[WorkStep]):
        name(str): name of executable
        todo: list with steps to run, if no steps are None, every step is
              executed
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    todo = prepare_process(todo, name, processes)

    success = True
    for step in workplan:
        name = step[NAME]
        # if todo is empty, nothing is selected, run every step
        if name not in todo and todo:
            log('skipping: %s' % name)
            continue
        else:
            log('processing: %s' % name)

        hook = step[HOOK]
        result = run_hook_safely(hook, name, step[OUTPUT])
        if result == FAILURE:
            # mark failure, but continue processing
            success = False
            continue

        result = write_result_safely(result, name, step[OUTPUT])
        if result == FAILURE:
            # mark failure, but process further
            success = False
    return SUCCESS if success else FAILURE


def input_order(plan):
    require = defaultdict(set)
    for step in plan:
        name = step['name']
        inputs = [str(item) for item in step['input']]

        for item in inputs:
            with suppress(ValueError):
                producer, _ = item.split('_', maxsplit=1)
                require[name].add(producer)
            continue
    order = determine_order(require, flat=False)
    return order


def parallelize_workplan(plan, max_processes=1):

    order = input_order(plan)

    steps = {step['name']: step for step in plan}
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


def prepare_hooks(items: List[FeatureInterface]):
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
        result.append('step:\n   %s' % item['name'])

        # prepare inputs
        result.append('inputs:')
        inputs = []
        for input_ in item['input']:
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
        for output_ in item['output']:
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


def run_hook_safely(hook: callable, name: str, stepoutput):
    try:
        result = hook()
    except Exception as msg:  # pylint: disable=broad-except
        log_stacktrace()
        error('while processing %s' % name)
        error(msg)
        return FAILURE

    if isinstance(result, str):
        result = [result]
    # Verify result
    if result and len(stepoutput) != len(result):
        error('wrong return value count')
        error('interface count %d' % len(stepoutput))
        error('return count from method %d' % len(result))
        return FAILURE
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


def find_features(root: str, featurepackage: str) -> List[FeatureInterface]:
    """Locate all feautures in given path

    Ensure that feature methods are defined. If some feature interface is not
    implemented properly, the exection ends with FAILURE.
    """
    featurepath = join(root, featurepackage.replace('.', '/'))
    assert exists(root), root
    collected = [
        item.replace('.py', '')
        for item in listdir(featurepath)
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
CommandLineInterface = List[Command]
Worker = callable  #pylint:disable=C0103
Feature = Tuple[Name, CommandLineInterface, Worker]


def commandline(features: List[Feature], workplan) -> List[Command]:
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
    result.append(Flag('--all'))

    return result


def create_step(
        name: str,
        inputs: List[Tuple[str]],
        output: Tuple[str],
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
    assert isinstance(inputs, List), '%s %s' % (type(inputs), str(inputs))
    assert isinstance(output, tuple), '%s %s' % (type(output), str(output))

    step = {
        NAME: name,
        INPUT: inputs,
        OUTPUT: output,
    }
    return step


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
) -> List[WorkStep]:
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
        inputs, outputs = step[INPUT], step[OUTPUT]
        variables = prepare_variables(variables=inputs, args=args)
        call_inputs = prepare_inputs(inputs, inspace, outspace)
        name = step[NAME]
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
            outputs=outputs,
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
        function_call = partial(caller, *call_inputs)

        result.append({
            NAME: name,
            HOOK: function_call,
            OUTPUT: outputs,
        })

    if ret and verify:
        exit(FAILURE)
    return result


def determine_variables(workplan):
    result = []
    for step in workplan:
        inputs = step[INPUT]
        for item in inputs:
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


def prepare_inputs(inputs, inspaces, outspace) -> List[str]:
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
                filepath = join(inspace, filename)
                if exists(filepath):
                    result.append(filepath)
                else:
                    # TODO: Refactor recursive inputs
                    # Only on the last inspace, because the file could exists
                    # in other input folder
                    if inspace == inspaces[-1]:
                        recursivepath = join(outspace, filename)
                        info('recursive input %s' % recursivepath)
                        result.append('_%s' % recursivepath)
            elif isinstance(item, File):
                filename = '%s.%s' % (name, ext)
                filepath = join(inspace, filename)
                if exists(filepath):
                    result.append(filepath)
                else:
                    if not lastinput:
                        continue
                    error('search location: %s' % search_location)
                    error('missing input: %s' % filepath)
            else:
                _, filename = split(inspace)
                if '.' in filename:
                    # File as a input name
                    result.append(inspace)
                else:
                    ext = ext.lower()
                    pattern = '%s/%s.%s' % (inspace, name, ext)
                    info('using pattern: %s' % pattern)
                    files = glob(pattern)
                    info('%s' % str(files))
                    for finding in files:
                        print('FINDING %s' % finding)
                        result.append(finding)

    call('result: %s\n' % result)
    return result


def prepare_outputs(
        process_: str,
        stepname: str,
        prefix: str,
        outputs: str,
        outspace: str,
) -> List[str]:
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
    outputs = [join(outspace, item) for item in _outputs]
    return outputs


def verify_resources(inputs):
    ret = 0
    # require input files
    for path in inputs:
        if exists(path):
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
    signatures = str(signature(worker))
    if worker.__name__ == 'wrapper' and signatures == '(*args, **kwds)':
        with suppress(AttributeError):
            # bypass wrapper of `typechecker.checkdatatype`
            worker = worker.__userfunc__

    call_parameter = signature(worker).parameters
    interface_error_msg = 'interface error %s != %s' % (
        list(call_parameter.keys()),
        inputs,
    )
    if not len(call_parameter) == len(inputs):
        error('missing input resources: %s' % interface_error_msg)
        return FAILURE

    # check output parameter
    return_parameter = str(signature(worker).return_annotation)
    return_count = return_parameter.count('str')
    interface_error_msg = 'interface error %s != %s' % (
        return_parameter,
        outputs,
    )
    if not len(outputs) == return_count:
        error('missing output resources: %s' % interface_error_msg)
        return FAILURE
    return SUCCESS


def determine_todo(args):
    args = dict(args)
    del args['input']
    del args['output']
    if not any(args.values()):
        # run all features
        result = [key for key, value in args.items()]
    else:
        # True is important!
        result = [key for key, value in args.items() if value == True]  # pylint:disable=singleton-comparison
    return result


@dataclass
class Input:
    pass


@dataclass
class Value(Input):
    name: str
    typ: str
    defaultvar: str
    minimum: str = ''
    maximum: str = ''

    def __repr__(self):
        ctor = ("Value(name='%s', typ='%s', defaultvar='%s',"
                " minimum='%s', maximum='%s')")
        return ctor % (
            self.name,
            self.typ,
            self.defaultvar,
            self.minimum,
            self.maximum,
        )


@dataclass
class Pattern(Input):
    name: str
    ext: str

    def __str__(self):
        return '%s.%s' % (self.name, self.ext)

    def __getitem__(self, index):
        # make pattern iterable
        return [self.name, self.ext][index]


@dataclass
class File(Pattern):
    ext: str = 'yaml'


@dataclass
class ResultFile(File):
    producer: str = 'default'

    def __str__(self):
        return '%s__%s.%s' % (self.producer, self.name, self.ext)
