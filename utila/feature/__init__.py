# TODO: SPLIT THIS MODULE
# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
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

requirements
------------

.. note :: TODO: SUPPORT ONLY ONE VARIABLE INPUT AND OUTPUT PARAMETER?
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
import textwrap
import typing

import utila
import utila.cli
import utila.feature.collector
import utila.feature.config
import utila.feature.description
import utila.feature.processor
import utila.utils

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
    workplan = read_workplan(
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
    # an empty workplan is defined by user code, feature pack does nothing
    if not workplan:
        utila.error('empty workplan - nothing todo - abort!')
        return utila.FAILURE

    # Ensure to have output folder
    os.makedirs(outputpath, exist_ok=True)

    current_todo = determine_todo(args, config.flags)
    completed = utila.feature.processor.process(
        workplan,
        config.name,
        errorhook=config.errorhook,
        failfast=failfast,
        pages=pages,
        processes=processes,
        todo=current_todo,
        profiling=profiling,
    )
    return completed


def commandline(
        features: Features,
        workplan: list,
) -> typing.List[utila.Command]:
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
    variables = determine_variables(workplan)
    variables = list(set(variables))  # avoid duplicating parameter
    for item in sorted(variables):
        result.append(utila.Parameter(longcut=item))

    # run all workplan feature
    result.append(utila.Flag(longcut='all'))

    return result


def create_step(
        name: str,
        inputs: typing.List['Input'],
        output: typing.Tuple[str],
) -> WorkStep:
    """Create a WorkStep from definition.

    Example:

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


def read_workplan(  # pylint:disable=too-many-locals
        plan: list,
        process_: str,
        hooks: dict,
        inspace: str,
        outspace: str = None,
        args: dict = None,
        prefix: str = None,
        verify: bool = False,
        used_processes: int = 1,
) -> typing.List[WorkStep]:
    """Parse user defined workplan

    Args:
        plan: list of working steps
        process_: step name to print on console
        hooks: dict of name and callable function
        inspace(str or list): list of input spaces
        outspace(str): absolute path to write output
        args: dict of additonal arguments
        prefix(str): to distingush different parameterization written in the
                     same folder
        verify(bool): if True, let execution failed on workplan error
        used_processes(int): maximum parallel used processes
    Returns:
        Parsed list of worksteps with verified inputs.
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
        if utila.PAGES_FLAG in [item.name for item in step.inputs]:
            utila.error(str(step.inputs))
            msg = 'parameter `pages` is not allowed in `workplan`, step: %s'
            utila.error(msg % step.name)
            ret += 1
            continue

        call_inputs = prepare_inputs(step.inputs, inspace, outspace)
        name = step.name
        try:
            caller = hooks[name]
        except KeyError:
            utila.error('missing hook with name %s' % name)
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
        if verify_interface(call_inputs, outputs, caller) == utila.FAILURE:
            ret += 1
            continue
        function_call = functools.partial(caller, *call_inputs)

        result.append(WorkStep(name, function_call, outputs))

    if ret and verify:
        exit(utila.FAILURE)
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
    order = utila.utils.determine_order(require, flat=False)
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
    """Extract variables out of inputs, ignore files and pattern."""
    result = []
    for variable in variables:
        if not isinstance(variable, utila.Value):
            continue
        typ = variable.typ
        if typ is bool:
            # convert cause every non empty string is converted to true
            typ = utila.utils.str2bool
        if typ is int:
            typ = utila.utils.str2int
        try:
            values = args[variable.name]
            defaultvalues = typ(variable.defaultvar)
            converted = typ(values) if values is not None else defaultvalues
            result.append(converted)
        except ValueError:
            msg = 'while processing %s with value %s'
            utila.error(msg % (variable.name, variable.typ))
            utila.error('given args %r' % args)
    return result


def prepare_inputs(  # pylint:disable=too-many-locals,too-complex,too-many-branches
        inputs: list,
        inspaces: list,
        outspace: str,
) -> typing.List[str]:
    """Parse single and multiple file input

    Locate files by defined pattern in `Workplan`. A file pattern is
    defined via (name, typ). The ext is in UPPER-CASES, for example (*,
    PDF) to locate multiple pdf's.

    Args:
        inputs(str): inputs are defined in a workplan
        inspaces(str): inspaces is the current input via -i
        outspace(str): path to write results and use as possible input
                       source for `recursive inputs`.
    Returns:
        List of located files.
    """

    utila.call('prepare inputs')
    result = []
    # single file input
    search_location = ' '.join(inspaces)
    for item in inputs:
        lastinput = item == inputs[-1]
        utila.info('skipping input `%s`, require `Pattern' % str(item))
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
                        utila.info('recursive input %s' % recursivepath)
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
                    utila.error('search location: %s' % search_location)
                    utila.error('missing input: %s' % filepath)
            else:
                _, filename = os.path.split(inspace)
                if '.' in filename and filename[0] != '.':  # .tmp
                    # .tmp is not a file name, it is a directory.
                    # File as a input name
                    result.append(inspace)
                    break  # do not double add path
                elif os.path.isfile(inspace):
                    # support dir-like file-path as input
                    # TODO: Introduce new datatype?
                    result.append(inspace)
                    break  # do not double add path
                else:
                    ext = ext.lower()
                    pattern = '%s/%s.%s' % (inspace, name, ext)
                    utila.info('using pattern: %s' % pattern)
                    files = glob.glob(pattern)
                    utila.info('%s' % str(files))
                    for finding in files:
                        utila.info('FINDING %s' % finding)
                        result.append(finding)
    utila.call(f'result: {result}')
    return result


def prepare_outputs(
        process_: str,
        stepname: str,
        prefix: str,
        outputs: list,
        outspace: str,
) -> typing.List[str]:
    """Support different output types

    Args:
        process_(str): name to invoke program by system call
        stepname(str): a step describes a part of working in the process
        prefix(str): optional to add prefix to differentiate output files
        outputs(list): list of items to write results of steps as files
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
                utila.error(f'checking output number {index}')
                msg = ('require tuple with (item, datatype).'
                       f' got: {item!r} {type(item)}')
                utila.error(msg)
                ret += 1
        outitem = f'{process_}__{prefix}{stepname}_{item}.{datatype}'
        _outputs.append(outitem)

    if ret:
        exit(utila.FAILURE)
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
        utila.error('File does not exists: %s' % path)
        ret += 1
    return ret


def verify_interface(inputs, outputs, worker):
    # check callable
    # check input parameter
    call_parameter = inspect.signature(worker).parameters
    parameter = [str(item) for item in call_parameter.values()]
    # variable name of input parameter
    dynamic_collection = len([item for item in parameter if '*' in item]) == 1
    if not dynamic_collection:
        # Optional pages flag, reduces count of required parameter in
        # definition.
        has_pages = int(utila.PAGES_FLAG in call_parameter)
        if not len(call_parameter) == len(inputs) + has_pages:
            utila.error(
                f'missing input resources: '
                f'interface error {list(call_parameter.keys())} != {inputs}')
            return utila.FAILURE

    # check output parameter
    return_parameter = str(inspect.signature(worker).return_annotation)
    return_count = return_parameter.count('str')

    variable_returnvalues = variable_parameter(outputs)
    if not len(outputs) == return_count and not variable_returnvalues:
        utila.error(f'missing output resources: '
                    f'interface error {return_parameter} != {outputs}')
        return utila.FAILURE
    return utila.SUCCESS


def variable_parameter(items: list) -> bool:
    """Check if some path contains *-pattern to replace."""
    result = any(['*' in item for item in items])
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
