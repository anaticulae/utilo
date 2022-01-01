# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses
import typing

import utila.feature


@dataclasses.dataclass  # pylint:disable=R0903
class Input:
    pass


@dataclasses.dataclass  # pylint:disable=R0903
class Bool(Input):
    name: str


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
    # TODO: EXCLUDE OPTIONAL AND RECURSIVE INPUT
    optional: bool = False

    def __str__(self):
        return '%s.%s' % (self.name, self.ext)

    def __getitem__(self, index):
        # make pattern iterable
        return [self.name, self.ext][index]


@dataclasses.dataclass  # pylint:disable=R0903
class File(Pattern):
    ext: str = 'yaml'


@dataclasses.dataclass  # pylint:disable=R0903
class Directory(Pattern):
    ext: str = ''

    def __str__(self):
        return self.name


@dataclasses.dataclass  # pylint:disable=R0903
class ResultFile(File):
    producer: str = 'default'

    def __init__(
        self,
        producer: str,
        name: str,
        ext: str = 'yaml',
        optional: bool = False,
    ):
        self.producer = producer
        self.name = name
        self.ext = ext
        self.optional = optional

    def __str__(self):
        if not self.name and not self.ext:
            return self.producer
        if not self.ext:
            return '%s__%s' % (self.producer, self.name)
        return '%s__%s.%s' % (self.producer, self.name, self.ext)


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


def create_step(
    name: str,
    inputs: typing.List['Input'] = None,
    output: typing.Tuple[str] = None,
) -> 'WorkPlanStep':
    """Create a WorkPlanStep from definition.

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
    if inputs is None:
        inputs = []
    if output is None:
        output = []
    assert isinstance(inputs, list), '%s %s' % (type(inputs), str(inputs))
    for index, item in enumerate(inputs):
        assert isinstance(item, Input), f'{index} {item}'
    msg = '%s %s' % (type(output), str(output))
    assert isinstance(output, (tuple, list)), msg
    return utila.WorkPlanStep(name, inputs, output)
