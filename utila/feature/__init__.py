# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
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
import collections
import contextlib
import dataclasses
import os
import typing

import utila
import utila.cli
import utila.feature.collector
import utila.feature.config
import utila.feature.description
import utila.feature.processor
import utila.feature.userinput

WorkStep = collections.namedtuple('WorkStep', 'name inputs outputs')
WorkSteps = typing.List[WorkStep]

Name = str
CommandLineInterface = typing.List[utila.Command]
Worker = callable  #pylint:disable=C0103
Feature = typing.Tuple[Name, CommandLineInterface, Worker]
Features = typing.List[Feature]


class InterfaceMismatch(TypeError):
    pass


@dataclasses.dataclass
class FeaturePackConfig:
    description: str = None
    errorhook: 'utila.feature.processor.ErrorHook' = None
    failfastflag: bool = True
    flags: list = dataclasses.field(default_factory=list)
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


@utila.saveme(systemexit=True)
def featurepack(  # pylint:disable=too-many-locals
        workplan: WorkSteps,
        root: str,
        featurepackage: str,
        config: FeaturePackConfig = None,
) -> int:
    """Run featurepack defined in `workplan`

    Args:
        workplan: define used features with in- and outpath
        root(str): path to project root
        featurepackage(str): location to featurepackage releative to root
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
    feature = utila.feature.collector.find_features(root, featurepackage)
    commands = commandline(feature, workplan)

    description = utila.feature.description.prepare_description(
        config.name,
        config.description,
        workplan,
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
    args = utila.parse(parser)
    # overwrite input as fast as possible. This is required to overwrite
    # general flags (profiling, failfast, etc.).
    utila.feature.config.overwrite(args)

    processes, failfast, pages, profiling = utila.cli.evaluate_flags(
        args,
        config.multiprocessed,
    )
    # evaluate the verbose flag
    inputpath, outputpath, prefix, verbose = utila.sources(
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

    hooks = utila.feature.collector.prepare_hooks(feature)

    prepared_workplan = utila.feature.workplan.read_workplan(
        workplan,
        process_=config.name,
        hooks=hooks,
        inspace=inputpath,
        outspace=outputpath,
        args=args,
        prefix=prefix,
        used_processes=processes,
        verify=True,
    )
    # ensure to handle selected steps correctly
    remove_workplan_flags(workplan, args)

    # Ensure to have output folder
    os.makedirs(outputpath, exist_ok=True)

    current_todo = determine_todo(args, config.flags)
    completed = utila.feature.processor.process(
        prepared_workplan,
        config.name,
        errorhook=config.errorhook,
        failfast=failfast,
        pages=pages,
        processes=processes,
        todo=current_todo,
        profiling=profiling,
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
    for _, command, _ in features:
        commands = command()
        # one single command is iterable, testing of Iterable is not possible
        if isinstance(commands, (list, tuple)):
            # support adding commands from iterable and single command
            result.extend(commands)
        else:
            result.append(commands)
    # add sorted, unique parameter as parameterization point
    variables = determine_instance(workplan, utila.feature.userinput.Value)
    for item in sorted(variables):
        result.append(utila.Parameter(longcut=item))
    # add sorted, unique flag as parameterization point
    flags = determine_instance(workplan, utila.feature.userinput.Bool)
    for item in sorted(flags):
        result.append(utila.Flag(longcut=item))

    # run all workplan feature
    result.append(utila.Flag(longcut='all'))

    return result


def remove_workplan_flags(plan, args):
    """Remove `Bool`-Flags which are part of the workplan steps to
    evaluate selected steps correctly."""
    collected = set()
    for step in plan:
        for variable in step.inputs:
            if isinstance(variable, utila.Bool):
                collected.add(variable.name)
    for item in collected:
        del args[item]


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


def variable_parameter(items: list) -> int:
    """Count number of path contains *-pattern to replace."""
    result = len([item for item in items if '*' in item])
    return result


def variable_datatype(items: list) -> int:
    """Count number of path ends with ???-pattern to replace datatype."""
    result = len([item for item in items if item.endswith('???')])
    return result


def determine_todo(args: dict, flags: list) -> typing.List[str]:
    """Remove flags from feature todo list

    Hint:
        See feature selection approach.

    Args:
        args(dict): user defined command line arguments
        flags(tuple or str): possible bool flag args for examle `--linter`
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

    if not any(args.values()):
        # run all features
        result = [key for key in args.keys()]
    else:
        # True is important!
        result = [key for key, value in args.items() if value == True]  # pylint:disable=singleton-comparison
    return result
