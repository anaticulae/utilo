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
from inspect import signature
from os import listdir
from os import makedirs
from os.path import exists
from os.path import join
from typing import List
from typing import Tuple

from utila.cmdline import create_parser
from utila.cmdline import parse
from utila.cmdline import sources
from utila.error import saveme
from utila.file import file_create
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
        feature_path: str,
        feature_package: str,
        name: str,
        description: str,
        version: str,
):
    feature = find_features(feature_path, feature_package)
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
    inputpath, outputpath, verbose = sources(args, verbose=True)
    if not inputpath or not outputpath:
        parser.print_usage()
        return FAILURE

    workplan = read_workplan(workplan, inputpath, outputpath, verify=True)

    # Ensure to have output folder
    makedirs(outputpath, exist_ok=True)

    completed = process(workplan, verbose=verbose)
    return completed


def process(
        workplan,
        verbose: bool = False,
):
    for step in workplan:
        name = step[NAME]
        logging('processing %s' % name)
        try:
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
                    # Write content to file.
                    file_create(path, content)
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


def find_features(path: str, feature_package):
    """Locate all feautures in given path
    """
    assert exists(path), path
    collected = [
        item.replace('.py', '')
        for item in listdir(path)
        if not '__init__' in item and item.endswith('.py')
    ]
    result = []
    ret = 0
    for item in collected:
        current = importlib.import_module(feature_package + '.' + item,
                                          feature_package)
        try:
            result.append((current.name(), current.commandline, current.work))
        except AttributeError as exception:
            logging_error('SKIP LOADING %s' % item)
            logging_error(exception)
            ret += 1
    if ret:
        exit(FAILURE)
    return result


def commandline(features):
    result = []

    # name, cmd, work
    for _, command, _ in features:
        result.append(command())

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


def read_workplan(plan, inspace, outspace=None, verify: bool = False):
    outspace = outspace if outspace else inspace

    result = []
    ret = 0
    for step in plan:
        inputs, outputs = step[INPUT], step[OUTPUT]
        name, caller = step[NAME], step[HOOK]

        inputs = ['%s__%s.yaml' % item for item in inputs]
        inputs = [join(inspace, item) for item in inputs]

        _outputs = []
        for item in outputs:
            datatype = 'yaml'
            if not isinstance(item, str):
                item, datatype = item

            _outputs.append('%s__%s.%s' % (name, item, datatype))
        outputs = [join(outspace, item) for item in _outputs]

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
