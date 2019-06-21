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
from functools import partial
from glob import glob
from inspect import signature
from os import listdir
from os import makedirs
from os.path import exists
from os.path import isfile
from os.path import join
from typing import List
from typing import Tuple

from utila.cmdline import Command
from utila.cmdline import Flag
from utila.cmdline import create_parser
from utila.cmdline import parse
from utila.cmdline import sources
from utila.error import saveme
from utila.file import file_replace
from utila.logging import logging
from utila.logging import logging_error
from utila.logging import logging_stacktrace
from utila.utils import FAILURE
from utila.utils import SUCCESS

NAME = 'name'
INPUT = 'input'
OUTPUT = 'output'
HOOK = 'hook'


@saveme(systemexit=True)
def featurepack(
        workplan,
        root: str,
        feature_package: str,
        name: str,
        description: str,
        version: str,
        singleinput: bool = False,
) -> int:
    """Run featurepack defined in `workplan`

    Args:
        workplan:
        root(str): path to project root
        feature_package(str): location to feature_package releative to root
        name(str): name to invoke cmdline tool
        description(str): description shown in cmdline tool
        version(str): version to display with --version command
        singleinput(bool): if true, files as input are allowed, else only
                           directories are allowed
    Returns:
        return SUCCESS or FAILURE
    """
    feature = find_features(root, feature_package)
    commands = commandline(feature)
    parser = create_parser(
        commands,
        prog=name,
        description=description,
        version=version,
        outputparameter=True,
        inputparameter=True,
    )
    args = parse(parser)

    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = sources(
        args,
        singleinput=singleinput,
        verbose=True,
    )
    current_todo = todo(args)
    if not inputpath or not outputpath:
        parser.print_usage()
        return FAILURE

    workplan = read_workplan(
        workplan,
        inputpath,
        outputpath,
        prefix=prefix,
        verify=True,
    )
    # an empty workplan is defined by user code, feature pack does nothing
    if not workplan:
        logging_error('empty workplan - nothing todo - abort!')
        exit(FAILURE)

    # Ensure to have output folder
    makedirs(outputpath, exist_ok=True)

    completed = process(
        workplan,
        todo=current_todo,
        verbose=verbose,
    )
    return completed


def process(
        workplan,
        todo: List = None,
        verbose: bool = False,
):
    """Process the given features

    Args:
        workplan(List[steps]):
        verbose(bool): extend logging verbosity
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    # TODO: add todo to select features
    if todo is None:
        todo = []
    todo = set(todo)
    for step in workplan:
        name = step[NAME]
        # TODO: change name to step name, not the process name
        # for example processing chapter, processing title, processing index...
        logging('processing %s' % name)
        try:
            if name not in todo and todo:
                # if todo is empty, nothing is selected, so run every step
                logging('Skipping %s' % name)
                continue

            hook = step[HOOK]
            result = hook()
            if isinstance(result, str):
                result = [result]
            if result and len(step[OUTPUT]) != len(result):
                logging_error('wrong return value count')
                logging_error('interface count %d' % len(step[OUTPUT]))
                logging_error('return count from method %d' % len(result))
                return FAILURE
            try:
                for path, content in zip(step[OUTPUT], result):
                    if verbose:
                        logging('write: %s' % path)
                    # write content to file.
                    file_replace(path, content)
            except TypeError as error:
                logging_error('while processing %s' % name)
                logging_error('wrong return value')
                logging_error('current return value: %s' % result)
                logging_error(error)
                return FAILURE
        except Exception as error:  # pylint: disable=broad-except
            logging_error('while processing %s' % name)
            logging_error(error)
            logging_stacktrace()
            return FAILURE
    return SUCCESS


def find_features(root: str, featurepackage):
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
            logging_error('SKIP LOADING %s' % item)
            logging_error(exception)
            ret += 1
    if ret:
        exit(FAILURE)
    return result


def connect_feature_interface(current, item):
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


def commandline(features: List[Feature]) -> List[Command]:
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
    return result


def create_step(
        name: str,
        hook: callable,
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
        HOOK: hook,
    }
    """
    assert isinstance(inputs, List), type(inputs)
    assert all([isinstance(item, tuple) for item in inputs])
    assert isinstance(output, tuple), type(output)

    step = {
        NAME: name,
        INPUT: inputs,
        OUTPUT: output,
        HOOK: hook,
    }
    return step


def read_workplan(
        plan,
        inspace,
        outspace=None,
        prefix: str = None,
        verify: bool = False,
):
    outspace = outspace if outspace else inspace
    prefix = '%s_' % prefix if prefix else ''

    result = []
    ret = 0
    for step in plan:
        inputs, outputs = step[INPUT], step[OUTPUT]
        inputs = prepare_inputs(inputs, inspace)

        name, caller = step[NAME], step[HOOK]
        outputs = prepare_outputs(name, prefix, outputs, outspace)

        verify_interface(inputs, outputs, caller)
        ret += verify_resources(inputs, outputs)

        function_call = partial(caller, *inputs)

        result.append({
            NAME: step[NAME],
            HOOK: function_call,
            OUTPUT: outputs,
        })

    if ret and verify:
        exit(FAILURE)

    return result


def prepare_inputs(inputs, inspace) -> List[str]:
    """Parse single and multiple file input

    Loacted files by defined pattern in `Workplan`. A file pattern is defined
    via (name, typ). The typ is written in UPPER-CASES, for example (*, PDF)
    to locate multiple pdf's.

    Args:
        inputs(str): inputs is deliverd by workplan
        inspace(str): inspace is the current input via -i/--input
    Returns:
        list of located files
    """
    result = []
    # single file input
    if isfile(inspace) and len(inputs) == 1:
        # TODO: Not stable for multiple inputs
        return [inspace]

    for item in inputs:
        (name, typ) = item
        if typ.isupper():
            typ = typ.lower()
            pattern = '%s/%s.%s' % (inspace, name, typ)
            for finding in glob(pattern):
                result.append(finding)
        else:
            filename = '%s__%s.yaml' % (name, typ)
            result.append(join(inspace, filename))
    return result


def prepare_outputs(
        stepname: str,
        prefix: str,
        outputs: str,
        outspace: str,
) -> List[str]:
    """Support different output types

    Args:
        stepname(str):
        prefix(str): optional to add prefix to differentiate output files
        outputs(str):
        outspace(str): folder to write results
    Returns:
        a list with paths to write output
    """
    _outputs = []
    for item in outputs:
        datatype = 'yaml'
        if not isinstance(item, str):
            item, datatype = item
        _outputs.append('%s__%s%s.%s' % (stepname, prefix, item, datatype))
    outputs = [join(outspace, item) for item in _outputs]
    return outputs


def verify_resources(inputs, outputs):

    ret = 0
    # require input files
    for path in inputs:
        if exists(path):
            continue
        logging_error('File does not exists: %s' % path)
        ret += 1

    # check that output does not exists
    for path in outputs:
        if not exists(path):
            continue
        logging_error('File exists: %s' % path)
        ret += 1
    return ret


def verify_interface(inputs, outputs, worker):
    # check callable
    # check input parameter
    # inputs = ['%s__%s.yaml' % item for item in inputs]
    call_parameter = signature(worker).parameters
    interface_error_msg = 'interface error %s != %s' % (
        list(call_parameter.keys()),
        inputs,
    )
    assert len(call_parameter) == len(inputs), interface_error_msg

    # check output parameter
    return_parameter = str(signature(worker).return_annotation)
    return_count = return_parameter.count('str')
    interface_error_msg = 'interface error %s != %s' % (
        return_parameter,
        outputs,
    )
    assert len(outputs) == return_count, interface_error_msg


def todo(args):
    args = dict(args)
    del args['input']
    del args['output']

    if not any(args.values()):
        # run all features
        result = [key for key, value in args.items()]
    else:
        result = [key for key, value in args.items() if value]
    return result
