# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import collections
import contextlib
import dataclasses
import os
import typing

import utila
import utila.feature.collector
import utila.feature.config
import utila.feature.description


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
    rename: callable = None
    version: str = None

    def __post_init__(self):
        if not self.cli_hook:
            return
        if not isinstance(self.cli_hook, list):
            self.cli_hook = [self.cli_hook]
        for (install, run) in self.cli_hook:
            install_signature = utila.attributes(install)
            run_signature = utila.attributes(run)
            msg = f'cli_hook: require `def install(parser):` hook {install_signature}'
            assert len(install_signature) >= 1, msg
            msg = f'cli_hook: require `def run(args):` hook {run_signature}'
            assert len(run_signature) >= 1, msg


Name = str
CommandLineInterface = typing.List[utila.Command]
Worker = callable  #pylint:disable=C0103
Feature = typing.Tuple[Name, CommandLineInterface, Worker]
Features = typing.List[Feature]


@utila.saveme(systemexit=True)
def featurepack(
    workplan: 'WorkPlanSteps',
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
    # parser
    parser = create_featurepack_parser(features, workplan, config)
    # evaluate cmd input
    choice = evaluate_userchoice(config, parser)
    runtime = utila.feature.workplan.create_runtime(
        workplan,
        process_=config.name,
        features=features,
        inspace=choice.inputpath,
        outspace=choice.outputpath,
        args=choice.args,
        prefix=choice.prefix,
        used_processes=choice.processes,
        verify=True,
    )
    # ensure to handle selected steps correctly
    args = remove_workplan_flags(choice.args, workplan)
    # Ensure to have output folder
    os.makedirs(choice.outputpath, exist_ok=True)
    current_todo = determine_todo(args, config.flags)
    cache = utila.feature.cache.cacheme if choice.usecache else utila.nothing
    with cache(config.name, config.version) as done:
        if done:
            # already cached
            return utila.SUCCESS
        profiles = utila.profile if choice.profiling else utila.nothing
        with profiles(config.name):
            completed = utila.feature.processor.process(
                runtime,
                name=config.name,
                errorhook=config.errorhook,
                before=config.before,
                after=config.after,
                failfast=choice.failfast,
                pages=choice.pages,
                processes=choice.processes,
                todo=current_todo,
                profiling=choice.profiling,
                argv=choice.argv,
                verbose=choice.verbose,
                wait=choice.wait,
                rename=config.rename,
            )
    return completed


def create_featurepack_parser(
    features,
    workplan,
    config,
) -> argparse.ArgumentParser:
    commands = commandline(features, workplan)
    configuration = utila.ParserConfiguration(
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
    description = utila.feature.description.prepare_description(
        config.name,
        config.description,
        workplan,
        features,
        rename=config.rename,
    )
    parser = utila.cli.create_parser(
        commands,
        config=configuration,
        description=description,
        prog=config.name,
        version=config.version,
    )
    return parser


UserChoice = collections.namedtuple(
    'UserChoice',
    'args, inputpath, outputpath, prefix, verbose processes, failfast, pages, '
    'profiling, wait, usecache, argv',
)


def evaluate_userchoice(config, parser) -> UserChoice:  # pylint:disable=R0914
    hooked = config.cli_hook if config.cli_hook else []
    for install, _ in hooked:
        # install optional parser steps
        install(parser)
    # evaluate create parser
    args = utila.parse(parser)
    optional_data = dict()
    for _, run in hooked:
        if not run:
            continue
        # run optional parser steps
        parsed = run(args)
        if parsed:
            optional_data = utila.dicts_united(optional_data, parsed)
    # overwrite input as fast as possible. This is required to overwrite
    # general flags (profiling, failfast, etc.).
    utila.feature.config.overwrite(args)
    processes, failfast, pages, profiling, wait = utila.cli.evaluate_flags(  # pylint:disable=W0613
        args,
        config.multiprocessed,
    )
    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = utila.sources(  # pylint:disable=unbalanced-tuple-unpacking
        args,
        singleinput=config.singleinput,
        verbose=True,
    )
    argv = dict(inputs=inputpath, outputs=outputpath, prefix=prefix)
    if optional_data:
        # add hooked data to automated vars
        argv = utila.dicts_united(argv, optional_data)
    # update logging level
    level = utila.Level(verbose)
    if args.get('quite', False):
        # suppress logging - log errors only
        level = utila.Level.ERROR
    utila.level_setup(level)
    usecache = args.get('cache', False)
    result = UserChoice(
        args,
        inputpath,
        outputpath,
        prefix,
        verbose,
        processes,
        failfast,
        pages,
        profiling,
        wait,
        usecache,
        argv,
    )
    return result


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
