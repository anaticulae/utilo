# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent
import functools
import inspect
import os
import typing

import utila
import utila.feature

ErrorHook = typing.Tuple[Exception, str]


def process(
        workplan: 'utila.feature.WorkSteps',
        name: str = None,
        todo: typing.List = None,
        processes: int = 1,
        pages: list = None,
        errorhook: ErrorHook = None,
        *,
        failfast: bool = False,
        profiling: bool = False,
) -> int:
    """Process the given features. The process ignores errors in
    sub-steps and run till the end. If some error occurs, the process
    returns an `FAILURE` after finishing. If the todo-list is empty,
    every single step is processed.

    Args:
        workplan(WorkSteps): list of defined WorkStep's
        name(str): name of executable
        todo: list with steps to run, if no steps are None, every step is
              executed.
        processes(int): maximal parallel exection steps
        pages(list): list with processed pages
        errorhook(ErrorHook): if Error occurrs write it to ErrorHook
        failfast(bool): quit after first failure
        profiling(bool): if True, runtime of every single step is logged
    Returns:
        SUCCESS if all features process successfully, if not FAILURE
    """
    todo = prepare_process(todo, name, processes)

    workplan = utila.feature.parallelize_workplan(
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
            results = run_level(
                level=level,
                todo=todo,
                pool=pool,
                pages=pages,
                profiling=profiling,
            )
            # write result
            failure += write_level_result(
                results,
                errorhook=errorhook,
                failfast=failfast,
            )
            if failfast and failure:
                return utila.FAILURE
    status = utila.FAILURE if failure else utila.SUCCESS
    return status


def run_level(level, todo, pool, pages, profiling):
    results = []
    for step in level:
        # if todo is empty, nothing is selected, run every step
        if step.name not in todo and todo:
            utila.log(f'skipping: {step.name}')
            continue

        future = pool.submit(
            callback,
            step.inputs,
            stepname=step.name,
            output=step.outputs,
            pages=pages,
            profiling=profiling,
        )
        results.append(future)
    return results


def callback(
        hook: callable,
        stepname: str,
        output,
        pages: list,
        profiling: bool,
) -> tuple:
    """Run processing step.

    Args:
        hook(callable): function to execute
        stepname(str): name of working step
        output(str): path to write step output
        pages(list): list of pages to processed
        profiling(bool): if True log callback runtime
    Returns:
        Tuple of result, stepname and output
    """
    utila.log(f'processing: {stepname}')
    # run runnable
    runnable = functools.partial(
        run_hook_safely,
        hook=hook,
        name=stepname,
        stepoutput=output,
        pages=pages,
    )
    try:
        contextmanager = utila.profile if profiling else utila.nothing
        with contextmanager(msg=stepname):
            result = runnable()
            utila.log(f'completed: {stepname}')
    except Exception as exception:  # pylint:disable=broad-except
        utila.error(f'failed: {stepname}')
        result = exception  # pylint:disable=R0204
    return [result, stepname, output]


def run_hook_safely(
        hook: callable,
        name: str,
        stepoutput,
        pages,
) -> int:
    """Verify interface, run hook and catch Exception and log problem if
    required.
    """
    sig = inspect.signature(hook)
    try:
        if utila.PAGES_FLAG in sig.parameters:
            # optional page numbers flag
            result = hook(pages=pages)
        else:
            result = hook()
    except Exception:  # pylint: disable=broad-except
        utila.error('while processing %s' % name)
        utila.log_stacktrace()
        raise

    if isinstance(result, str):
        result = [result]
    # Verify result
    variable_returnvalues = utila.feature.variable_parameter(stepoutput)
    if result and len(stepoutput) != len(result) and not variable_returnvalues:
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
        utila.log('use multiple processes')
    utila.log()
    return todo


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
                return utila.FAILURE
        else:
            written = write_result_safely(*completed)
            if written == utila.FAILURE:
                success = False
                if failfast:
                    return utila.FAILURE
    return utila.SUCCESS if success else utila.FAILURE


def write_result_safely(
        result: typing.List[str],
        processstep: str,
        outputstep: typing.List[str],
) -> int:
    """Write `result`s to desired `outputstep`s and catch problems.

    Args:
        result(list): list of content to write
        processstep(name): name of process step
        outputstep(list): list of output paths
    Returns:
        Returns return code SUCCESS or FAILURE.
    """
    utila.call('write results')
    try:
        variable_returnvalues = utila.feature.variable_parameter(outputstep)
        if variable_returnvalues:
            assert len(outputstep) == 1, (f'only one variable parameter '
                                          f'is supported {outputstep}')
            outputstep = outputstep[0]
            # Create parent folder if required:
            # cli_example__multistep_pages/view_*.html
            # adding list of files in parent folder is possible.
            parent, _ = os.path.split(outputstep)
            os.makedirs(parent, exist_ok=True)
            # replace star-pattern to archive indexed output paths
            outputstep = [
                outputstep.replace('*', f'{index}')
                for index, content in enumerate(result)
            ]
        for path, content in zip(outputstep, result):
            # Ensure that parent folder exists. It is possible to create
            # folder via `hello/folder/content.txt`.
            parent, _ = os.path.split(path)
            os.makedirs(parent, exist_ok=True)
            utila.info('write %s' % path)
            # write content to file.
            utila.file_replace(path, content)
        return utila.SUCCESS
    except TypeError as msg:
        utila.error(f'while processing {processstep}')
        utila.error('wrong return value')
        utila.error(f'current return value: {result}')
        utila.error(msg)
        return utila.FAILURE


def select_executor():
    # TODO: how to use multiprocessing with pytest, see pytest: 38.3.1
    testrun = os.environ.get('PYTEST_PLUGINS', False)
    executor = concurrent.futures.ProcessPoolExecutor
    if testrun:
        executor = concurrent.futures.ThreadPoolExecutor
    return executor
