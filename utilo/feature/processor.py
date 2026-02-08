# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import functools
import os
import signal
import time

import utilo
import utilo.feature
import utilo.feature.outpath
import utilo.feature.workplan

ErrorHook = tuple[Exception, str]

NO_RESULT = object()


def process(  # pylint:disable=R0913,R0914,R1260
    workplan: 'ProcessSteps',
    name: str = None,
    todo: list = None,
    processes: int = 1,
    pages: list = None,
    errorhook: ErrorHook = None,
    rename: callable = None,
    before: callable = None,
    after: callable = None,
    ctrlbreak: callable = None,
    argv=None,
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
        argv(dict): magics defined in command line tool
        wait(int): if required, wait till incoming resources are ready
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    # TODO: CONVERT INTO A CLASS TO REDUCE COMPLEXITY
    executor = select_executor()
    if executor == concurrent.futures.ThreadPoolExecutor:
        # we do not require intializer with signal
        initializer = None
    else:
        register_signals(ctrlbreak)
        initializer = functools.partial(register_signals, ctrlbreak)
    todo = prepare_process(todo, name, processes, steps=len(workplan))
    if todo:
        # remove non selected items. Removing inactivate items is required
        # to determine the levels correctly. Why?
        # If we use 2 processes and we select --text and --font, the algo
        # run font first and afterwards text causes it thinks to run the
        # other inactivate levels.
        workplan = [item for item in workplan if item.name in todo]
    workplan = utilo.feature.workplan.parallelize(
        workplan,
        root=name,
        max_processes=processes,
    )
    pipeline = Pipeline()
    if not argv:
        argv = dict(pipeline=pipeline)
    else:
        argv['pipeline'] = pipeline
    with executor(max_workers=processes, initializer=initializer) as pool:
        failure = 0
        if before:
            befored = before()
            if befored:
                utilo.error('could not complete before')
                failure += befored
            if failfast and failure:
                return utilo.FAILURE
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
                argv=argv,
            )
            # write result
            failure += write_level_result(
                results,
                errorhook=errorhook,
                failfast=failfast,
                rename=rename,
            )
            if failfast and failure:
                return utilo.FAILURE
        if after:
            aftered = after()
            if aftered:
                utilo.error('could not complete after')
                failure += aftered
    status = utilo.FAILURE if failure else utilo.SUCCESS
    return status


class InterfaceMismatch(TypeError):
    pass


def run_level(
    level,
    todo,
    pool,
    pages,
    profiling,
    verbose: bool = True,
    wait: int = 0,
    argv=None,
):
    results = []
    for step in level:
        # if todo is empty, nothing is selected, run every step
        if step.name not in todo and todo:
            if verbose:
                utilo.log(f'skipping: {step.name}')
            continue
        future = pool.submit(
            callback,
            hook=step.hooks,
            stepname=step.name,
            output=step.outputs,
            pages=pages,
            profiling=profiling,
            wait=wait,
            argv=argv,
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
    argv=None,
) -> tuple:
    """Run processing step.

    Args:
        hook(callable): function to execute
        stepname(str): name of working step
        output(str): path to write step output
        pages(list): list of pages to processed
        profiling(bool): if True log callback runtime
        wait(int): seconds to wait for required input-resources
        argv(dict): magics defined in command line tool
    Returns:
        Tuple of result, stepname and output
    """
    utilo.log(f'processing: {stepname}')
    # wait = -1 run forever
    while require_wait(hook.work.args) and wait:  # pylint:disable=W0149
        utilo.log('.', end='')
        wait -= 1
        time.sleep(1)
    profiler = utilo.profile if profiling else utilo.nothing
    with profiler(msg=stepname, always=True):
        try:
            # run runnable
            result = run_hook_safely(
                hook=hook,
                name=stepname,
                stepoutput=output,
                pages=pages,
                argv=argv,
            )
            utilo.log(f'completed: {stepname}')
        except Exception as exception:  # pylint:disable=broad-except
            utilo.error(f'failed: {stepname}')
            utilo.error(exception)
            if hook.error:
                hook.error(stepname, exception)
            result = exception  # pylint:disable=R0204
    return [result, stepname, output]


def require_wait(inputs: list) -> bool:
    return any((not utilo.exists(item) for item in inputs))


def run_hook_safely(
    hook: callable,
    name: str,
    stepoutput,
    pages,
    argv,
) -> int:
    """Verify interface, run hook and catch Exception.

    Log problem if required.
    """
    try:
        # run optional before hook before running work
        if hook.before:
            hook.before()
        result = utilo.pass_required(caller=hook.work, pages=pages, **argv)
        # run optional after hook after completing work
        if hook.after:
            hook.after()
    except Exception:  # pylint: disable=broad-except
        utilo.error(f'while processing {name}')
        utilo.print_stacktrace()
        raise
    if isinstance(result, (str, bytes)) or result == NO_RESULT:
        result = [result]
    if result == [NO_RESULT]:
        # TODO: UNITE WITH LINE -3
        result = []
    # Verify result
    variable_returnvalues = utilo.feature.outpath.variable_parameter(stepoutput)
    variable_datatype = utilo.feature.outpath.variable_datatype(stepoutput)
    result_length = len(result) - variable_datatype
    if all((
            result,
            len(stepoutput) != result_length,
            not variable_returnvalues,
    )):
        utilo.error(f'wrong return value count in step: `{name}`')
        utilo.error(f'interface count: {len(stepoutput)}')
        utilo.error(f'return count from step: {len(result)}')
        raise InterfaceMismatch
    return result


def prepare_process(todo, name, processes, steps: int):
    # make todo unique
    todo = set() if todo is None else set(todo)
    # process all features, see some lines below
    if 'all' in todo:
        todo = set()
    # log start of executable
    utilo.log(name)
    if processes > 1:
        processes = min((processes, steps))
        utilo.log(f'use {processes} processes')
    utilo.log()
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
        result, name = completed[0:2]
        if isinstance(result, Exception):
            if errorhook:
                errorhook(result, name)
            success = False
            if failfast:
                return utilo.FAILURE
        else:
            written = write_result_safely(
                *completed,
                rename=rename,
            )
            if written == utilo.FAILURE:
                success = False
                if failfast:
                    return utilo.FAILURE
    return utilo.SUCCESS if success else utilo.FAILURE


def write_result_safely(
    result: list[str],
    processstep: str,
    outputstep: list[str],
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
    utilo.call('write results')
    try:
        outputstep, result = utilo.feature.outpath.prepare_outputpath(
            outputstep,
            result,
            rename=rename,
        )
        for path, content in zip(outputstep, result):
            if content == NO_RESULT:
                continue
            write_resource(path, content, rename=rename)
        return utilo.SUCCESS
    except TypeError as msg:
        utilo.error(f'while processing {processstep}')
        utilo.error('wrong return value')
        utilo.error(utilo.shrink(result, maxlength=100))
        utilo.error(msg)
        return utilo.FAILURE


def write_resource(path, content, rename: callable = None):
    if not isinstance(path, str):
        # multiple resource
        for first, second in zip(path, content):
            write_resource(first, second, rename=rename)
        return
    if content.__class__.__name__ == 'object':
        utilo.log(f'no result, skip writing: {path}')
        return
    # Rename via rename-hook
    if rename:
        path = rename(path)
    # Ensure that parent folder exists. It is possible to create folder
    # via `hello/folder/content.txt`.
    parent = utilo.path_parent(path)
    os.makedirs(parent, exist_ok=True)
    utilo.info(f'write {path}')
    # write content to file.
    if isinstance(content, str):
        utilo.file_replace(path, content)
        return
    if isinstance(content, bytes):
        utilo.file_replace_binary(path, content)
        return
    if content == [NO_RESULT]:
        return
    msg = f'invalid content type: {type(content)}\nutilo.shrink(content)'
    utilo.exitx(msg)


def select_executor():
    # TODO: how to use multiprocessing with pytest, see pytest: 38.3.1
    executor = concurrent.futures.ProcessPoolExecutor
    if utilo.testing():
        executor = concurrent.futures.ThreadPoolExecutor
    return executor


def register_signals(ctrlbreak=None):
    if ctrlbreak is None:

        def ctrlbreak(event, name):  # pylint:disable=W0613
            # do nothing if signal handler is not defined
            return True

    if utilo.iswin():
        signal.signal(signal.SIGBREAK, ctrlbreak)  # pylint:disable=E1101
    else:
        pass
        # TODO: IS THIS REQUIRED?
        # THINK ABOUT THIS:
        # signal.SIGINT
        # Interrupt from keyboard (CTRL + C).


class Pipeline:
    """\
    >>> pipe = Pipeline()
    >>> pipe.run(sum, 20, 35, start=5)
    60
    >>> pipe.run(sum, 20, 35, start=5)
    60
    """

    def __init__(self):
        self.done = {}
        self.lock = utilo.Nothing()
        # TODO: ENABLE AFTER KNOWING HOW TO TO IT
        # manager = multiprocessing.Manager()
        # self.done = manager.dict()
        # self.lock = manager.RLock()

    def run(self, method, *argv, **kwargs):
        identifier = hash(str(method) + str(argv) + str(kwargs))
        with self.lock:
            try:
                return self.done[identifier]
            except KeyError:
                self.done[identifier] = method(argv, **kwargs)
            return self.done[identifier]
