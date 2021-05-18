# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""FeaturePack
===========

HowToUse
--------

todo!

requirements
------------

.. note :: TODO: SUPPORT ONLY ONE VARIABLE INPUT AND OUTPUT PARAMETER?

"""

import contextlib
import dataclasses
import inspect
import os
import sys
import typing
import zipfile

import utila
import utila.cli
import utila.feature.cache
import utila.feature.collector
import utila.feature.config
import utila.feature.description
import utila.feature.processor
import utila.feature.userinput

RESERVED_WORKPLAN_NAMES = {
    'all', 'cache', 'ff', 'i', 'input', 'j', 'jobs', 'o', 'output', 'pages',
    'prefix', 'wait'
}


@dataclasses.dataclass
class WorkPlanStep:
    name: str
    inputs: list = dataclasses.field(default_factory=list)
    outputs: list = dataclasses.field(default_factory=list)

    def __post_init__(self):
        assert self.name.lower() not in RESERVED_WORKPLAN_NAMES, (
            f'reserved workstep name: {self.name.lower()}')


WorkPlanSteps = typing.List[WorkPlanStep]

Name = str
CommandLineInterface = typing.List[utila.Command]
Worker = callable  #pylint:disable=C0103
Feature = typing.Tuple[Name, CommandLineInterface, Worker]
Features = typing.List[Feature]


@dataclasses.dataclass
class ProcessStep:
    name: str = None
    outputs: list = dataclasses.field(default_factory=list)
    hooks: 'utila.feature.collector.FeatureHooks' = None


ProcessSteps = typing.List[ProcessStep]


class InterfaceMismatch(TypeError):
    pass


@dataclasses.dataclass
class FeaturePackConfig:  # pylint:disable=too-many-instance-attributes
    description: str = None
    errorhook: 'utila.feature.processor.ErrorHook' = None
    before: callable = None
    after: callable = None
    failfastflag: bool = True
    flags: list = dataclasses.field(default_factory=list)
    cli_hook: tuple = None
    multiprocessed: bool = False
    name: str = None
    pages: bool = False
    prefixflag: bool = True
    profileflag: bool = False
    quiteflag: bool = False
    singleinput: bool = False
    verboseflag: bool = True
    configflag: bool = False
    version: str = None

    def __post_init__(self):
        if self.cli_hook:
            install, run = self.cli_hook  # pylint:disable=E0633
            install_signature = list(inspect.signature(install).parameters.keys()) # yapf:disable
            run_signature = list(inspect.signature(run).parameters.keys())
            msg = f'cli_hook: require `def install(parser):` hook {install_signature}'
            assert len(install_signature) >= 1, msg
            msg = f'cli_hook: require `def run(args):` hook {run_signature}'
            assert len(run_signature) >= 1, msg


@utila.saveme(systemexit=True)
def featurepack(  # pylint:disable=too-many-locals
    workplan: WorkPlanSteps,
    root: str,
    featurepackage: str,
    config: FeaturePackConfig = None,
) -> int:
    """Run featurepack defined in `workplan`

    Args:
        workplan: define selected features with in- and outpath
        root(str): path to project root
        featurepackage(str): location to featurepackage relative to root
        config(FeaturePackConfig): define featurepack behavior
    Returns:
        return SUCCESS or FAILURE
    """
    if config is None:
        FeaturePackConfig()
    # an empty workplan is defined by user code, feature pack does nothing
    if not workplan:
        utila.error('empty workplan - nothing todo - abort!')
        return utila.FAILURE
    features = utila.feature.collector.find_features(root, featurepackage)
    commands = commandline(features, workplan)

    description = utila.feature.description.prepare_description(
        config.name,
        config.description,
        workplan,
        features,
    )
    parser_configuration = utila.ParserConfiguration(
        failfastflag=config.failfastflag,
        flags=config.flags,
        inputparameter=True,
        multiprocessed=config.multiprocessed,
        outputparameter=True,
        pages=config.pages,
        prefix=config.prefixflag,
        profileflag=config.profileflag,
        quiteflag=config.quiteflag,
        verboseflag=config.verboseflag,
        configflag=config.configflag,
    )
    parser = utila.cli.create_parser(
        commands,
        config=parser_configuration,
        description=description,
        prog=config.name,
        version=config.version,
    )
    if config.cli_hook:
        install, run = config.cli_hook
    else:
        install, run = None, None
    if install:
        # install optional parser steps
        install(parser)
    # evaluate create parser
    args = utila.parse(parser)
    if run:
        # run optional parser steps
        run(args)  # pylint:disable=E1102
    # overwrite input as fast as possible. This is required to overwrite
    # general flags (profiling, failfast, etc.).
    utila.feature.config.overwrite(args)

    processes, failfast, pages, profiling, wait = utila.cli.evaluate_flags(
        args,
        config.multiprocessed,
    )
    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = utila.sources(  # pylint:disable=unbalanced-tuple-unpacking
        args,
        singleinput=config.singleinput,
        verbose=True,
    )

    # update logging level
    level = utila.Level(verbose)
    with contextlib.suppress(KeyError):
        if args['quite']:
            # suppress logging - log only errors
            level = utila.Level.ERROR
    utila.level_setup(level)

    runtime = utila.feature.workplan.create_runtime(
        workplan,
        process_=config.name,
        features=features,
        inspace=inputpath,
        outspace=outputpath,
        args=args,
        prefix=prefix,
        used_processes=processes,
        verify=True,
    )
    # ensure to handle selected steps correctly
    args = remove_workplan_flags(args, workplan)

    # Ensure to have output folder
    os.makedirs(outputpath, exist_ok=True)

    current_todo = determine_todo(args, config.flags)

    usecache = args.get('cache', False)
    cache = utila.feature.cache.cacheme if usecache else utila.nothing
    with cache(config.name, config.version) as done:
        if done:
            # already cached
            return utila.SUCCESS
        with utila.profile(config.name) if profiling else utila.nothing():
            completed = utila.feature.processor.process(
                runtime,
                config.name,
                errorhook=config.errorhook,
                before=config.before,
                after=config.after,
                failfast=failfast,
                pages=pages,
                processes=processes,
                todo=current_todo,
                profiling=profiling,
                verbose=verbose,
                wait=wait,
            )
    return completed


def commandline(features: Features, workplan: list) -> utila.Commands:
    """Build command line interface due iterating searched features

    Args:
        features: list of parsed features
        workplan: list with steps with in- and outputs
    Returns:
        list of `Command`s
    """
    result = []
    # name, cmd, work
    for feature in features:
        commands = feature.command()
        # one single command is iterable, testing of Iterable is not possible
        if isinstance(commands, (list, tuple)):
            # support adding commands from iterable and single command
            result.extend(commands)
        else:
            result.append(commands)
    # add sorted, unique parameter as parametrization point
    variables = determine_instance(workplan, utila.feature.userinput.Value)
    for item in sorted(variables):
        result.append(utila.Parameter(longcut=item))
    # add sorted, unique flag as parametrization point
    flags = determine_instance(workplan, utila.feature.userinput.Bool)
    for item in sorted(flags):
        result.append(utila.Flag(longcut=item))

    # run all workplan feature
    result.append(utila.Flag(longcut='all'))

    return result


def remove_workplan_flags(args, plan):
    """Remove `Bool`-Flags which are part of the workplan steps to
    evaluate selected steps correctly."""
    args = dict(args.items())
    collected = set()
    for step in plan:
        for variable in step.inputs:
            if isinstance(variable, utila.Bool):
                collected.add(variable.name)
    for item in collected:
        del args[item]
    return args


def determine_instance(workplan, typ):
    # avoid duplicating parameter
    result = set()
    for step in workplan:
        for item in step.inputs:
            if not isinstance(item, typ):
                continue
            result.add(item.name)
    result = list(result)  # pylint:disable=R0204
    result = sorted(result)
    return result


def determine_todo(args: dict, flags: list) -> typing.List[str]:
    """Remove flags from feature todo list

    Hint:
        See feature selection approach.

    Args:
        args(dict): user defined command line arguments
        flags(tuple or str): possible bool flag args for example `--linter`
    Returns:
        args list without possible flag-args
    """
    args = dict(args)
    del args['input']
    del args['output']

    def remove_bool_flags(cli_args, flags):
        # We have to remove all flags, which are not possible `to do`
        # flags. The `to do` mechanism run all features if no to do flag
        # is passed. If one flag is left, which is not related to todo
        # flag like `--linter_writing` every todo-job is skipped,
        # therefore we have to remove all external flags.
        for item in flags:
            try:
                flag, _ = item
            except ValueError:
                flag = item
            flag = utila.userflag_to_arg(flag)
            with contextlib.suppress(KeyError):
                # remove present user flags.
                del cli_args[flag]
        return cli_args

    args = remove_bool_flags(args, flags)

    all_selected = args.get('all', False)
    deactivated = [
        key for key, value in args.items() if value is utila.cli.DEACTIVATED
    ]
    seletected = any(item for item in args.values() if item is True)
    if not seletected or all_selected:
        # run all features
        result = [key for key, value in args.items()]
    else:
        # True is important!
        result = [key for key, value in args.items() if value == True]  # pylint:disable=singleton-comparison
    if deactivated or all_selected:
        # None is important:
        #   None means feature is actively disabled by user.
        #   False means feature is not selected.
        for item in deactivated + ['all']:
            with contextlib.suppress(ValueError):
                result.remove(item)
    return result
