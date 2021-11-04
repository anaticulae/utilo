# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import functools
import os
import signal
import sys
import time
import typing

import utila
import utila.feature
import utila.feature.outpath
import utila.feature.workplan

ErrorHook = typing.Tuple[Exception, str]

NO_RESULT = object()


def process(  # pylint:disable=R0914
    workplan: 'utila.feature.ProcessSteps',
    name: str = None,
    todo: typing.List = None,
    processes: int = 1,
    pages: list = None,
    errorhook: ErrorHook = None,
    rename: callable = None,
    before: callable = None,
    after: callable = None,
    ctrlbreak: callable = None,
    *,
    failfast: bool = False,
    profiling: bool = False,
    verbose: bool = False,
    wait: int = 0,
) -> int:
    """Process the given features. The process ignores errors in
    sub-steps and run till the end. If some error occurs, the process
    returns an `FAILURE` after finishing. If the todo-list is empty,
    every single step is processed.

    Args:
        workplan(WorkPlanSteps): list of defined WorkPlanStep's
        name(str): name of executable
        todo: list with steps to run, if no steps are None, every step is
              executed.
        processes(int): maximal parallel execution steps
        pages(list): list with processed pages
        errorhook(ErrorHook): if Error occurs write it to ErrorHook
        rename(callable): rename outputs
        before(callable): run before process plan
        after(callable): run before process plan
        ctrlbreak(callable): run if ctrl and break is pressed
        failfast(bool): quit after first failure
        profiling(bool): if True, runtime of every single step is logged
        verbose(bool): if True, print more logging information(skipped steps)
        wait(int): if required, wait till incoming resources are ready
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    executor = select_executor()
    if executor == concurrent.futures.ThreadPoolExecutor:
        # we do not require intializer with signal
        initializer = None
    else:
        register_signals(ctrlbreak)
        initializer = functools.partial(register_signals, ctrlbreak)
    todo = prepare_process(todo, name, processes)
    if todo:
        # remove non selected items. Removing inactivate items is required
        # to determine the levels correctly. Why?
        # If we use 2 processes and we select --text and --font, the algo
        # run font first and afterwards text causes it thinks to run the
        # other inactivate levels.
        workplan = [item for item in workplan if item.name in todo]
    workplan = utila.feature.workplan.parallelize(
        workplan,
        root=name,
        max_processes=processes,
    )
    with executor(max_workers=processes, initializer=initializer) as pool:
        failure = 0
        if before:
            befored = before()
            if befored:
                utila.error('could not complete before')
                failure += befored
            if failfast and failure:
                return utila.FAILURE
        for level in workplan:
            # wait that level finishes without waiting, a next level which
            # require resource of the current may will not find the
            # resource, cause the execution is not done.
            results = run_level(
                level=level,
                pages=pages,
                pool=pool,
                profiling=profiling,
                todo=todo,
                verbose=verbose,
                wait=wait,
            )
            # write result
            failure += write_level_result(
                results,
                errorhook=errorhook,
                failfast=failfast,
                rename=rename,
            )
            if failfast and failure:
                return utila.FAILURE
        if after:
            aftered = after()
            if aftered:
                utila.error('could not complete after')
                failure += aftered
    status = utila.FAILURE if failure else utila.SUCCESS
    return status


def register_signals(ctrlbreak=None):
    if ctrlbreak is None:

        def ctrlbreak(event, name):  # pylint:disable=W0613
            # do nothing if signal handler is not defined
            return True

    signal.signal(signal.SIGBREAK, ctrlbreak)


def run_level(
    level,
    todo,
    pool,
    pages,
    profiling,
    verbose: bool = True,
    wait: int = 0,
):
    results = []
    for step in level:
        # if todo is empty, nothing is selected, run every step
        if step.name not in todo and todo:
            if verbose:
                utila.log(f'skipping: {step.name}')
            continue
        future = pool.submit(
            callback,
            hook=step.hooks,
            stepname=step.name,
            output=step.outputs,
            pages=pages,
            profiling=profiling,
            wait=wait,
        )
        results.append(future)
    return results


def callback(
    hook: callable,
    stepname: str,
    output,
    pages: list,
    profiling: bool,
    wait: int = 0,
) -> tuple:
    """Run processing step.

    Args:
        hook(callable): function to execute
        stepname(str): name of working step
        output(str): path to write step output
        pages(list): list of pages to processed
        profiling(bool): if True log callback runtime
        wait(int): seconds to wait for required input-resources
    Returns:
        Tuple of result, stepname and output
    """
    utila.log(f'processing: {stepname}')
    # wait = -1 run forever
    while require_wait(hook.work.args) and wait:
        utila.log('.', end='')
        wait -= 1
        time.sleep(1)
    # run runnable
    runnable = functools.partial(
        run_hook_safely,
        hook=hook,
        name=stepname,
        stepoutput=output,
        pages=pages,
    )
    with utila.profile(msg=stepname) if profiling else utila.nothing():
        try:
            result = runnable()
            utila.log(f'completed: {stepname}')
        except Exception as exception:  # pylint:disable=broad-except
            utila.error(f'failed: {stepname}')
            utila.error(exception)
            if hook.error:
                hook.error(stepname, exception)
            result = exception  # pylint:disable=R0204
    return [result, stepname, output]


def require_wait(inputs: list) -> bool:
    for item in inputs:
        if not utila.exists(item):
            return True
    return False


def run_hook_safely(
    hook: callable,
    name: str,
    stepoutput,
    pages,
) -> int:
    """Verify interface, run hook and catch Exception and log problem if
    required.
    """
    try:
        # run optional before hook before running work
        if hook.before:
            hook.before()
        result = utila.pass_required(caller=hook.work, pages=pages)
        # run optional after hook after completing work
        if hook.after:
            hook.after()
    except Exception:  # pylint: disable=broad-except
        utila.error('while processing %s' % name)
        utila.print_stacktrace()
        raise
    if isinstance(result, (str, bytes)) or result == NO_RESULT:
        result = [result]
    # Verify result
    variable_returnvalues = utila.feature.outpath.variable_parameter(stepoutput)
    variable_datatype = utila.feature.outpath.variable_datatype(stepoutput)
    result_length = len(result) - variable_datatype
    if all((
            result,
            len(stepoutput) != result_length,
            not variable_returnvalues,
    )):
        utila.error(f'wrong return value count in step: `{name}`')
        utila.error(f'interface count: {len(stepoutput)}')
        utila.error(f'return count from step: {len(result)}')
        raise utila.feature.InterfaceMismatch
    return result


def prepare_process(todo, name, processes):
    # make todo unique
    todo = set() if todo is None else set(todo)
    # process all features, see some lines below
    if 'all' in todo:
        todo = set()
    # log start of executable
    utila.log(name)
    if processes > 1:
        utila.log(f'use {processes} processes')
    utila.log()
    return todo


def write_level_result(
    results,
    errorhook: ErrorHook = None,
    *,
    failfast=False,
    rename: callable = None,
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
                return utila.FAILURE
        else:
            written = write_result_safely(
                *completed,
                rename=rename,
            )
            if written == utila.FAILURE:
                success = False
                if failfast:
                    return utila.FAILURE
    return utila.SUCCESS if success else utila.FAILURE


def write_result_safely(
    result: typing.List[str],
    processstep: str,
    outputstep: typing.List[str],
    rename: callable = None,
) -> int:
    """Write `result`s to desired `outputstep`s and catch problems.

    Args:
        result(list): list of content to write
        processstep(name): name of process step
        outputstep(list): list of output paths
        rename(callable): rename outpath before writing
    Returns:
        Returns return code SUCCESS or FAILURE.
    """
    utila.call('write results')
    try:
        outputstep, result = utila.feature.outpath.prepare_outputpath(
            outputstep,
            result,
            rename=rename,
        )
        for path, content in zip(outputstep, result):
            write_resource(path, content, rename=rename)
        return utila.SUCCESS
    except TypeError as msg:
        utila.error(f'while processing {processstep}')
        utila.error('wrong return value')
        utila.error(utila.shrink(result, maxlength=100))
        utila.error(msg)
        return utila.FAILURE


def write_resource(path, content, rename: callable = None):
    if not isinstance(path, str):
        # multiple resource
        for first, second in zip(path, content):
            write_resource(first, second, rename=rename)
        return
    if content.__class__.__name__ == 'object':
        utila.log(f'no result, skip writing: {path}')
        return
    # Rename via rename-hook
    if rename:
        path = rename(path)
    # Ensure that parent folder exists. It is possible to create folder
    # via `hello/folder/content.txt`.
    parent, _ = os.path.split(path)
    os.makedirs(parent, exist_ok=True)
    utila.info(f'write {path}')
    # write content to file.
    if isinstance(content, str):
        utila.file_replace(path, content)
        return
    if isinstance(content, bytes):
        utila.file_replace_binary(path, content)
        return
    if content == [NO_RESULT]:
        return
    utila.error(f'invalid content type: {type(content)}')
    utila.error(utila.shrink(content))
    sys.exit(utila.FAILURE)


def select_executor():
    # TODO: how to use multiprocessing with pytest, see pytest: 38.3.1
    testrun = os.environ.get('PYTEST_PLUGINS', False)
    executor = concurrent.futures.ProcessPoolExecutor
    if testrun:
        executor = concurrent.futures.ThreadPoolExecutor
    return executor
