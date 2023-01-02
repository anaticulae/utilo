# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses

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
        return f'{self.name}.{self.ext}'

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
        super().__init__(
            name=name,
            ext=ext,
            optional=optional,
        )
        self.producer = producer

    def __str__(self):
        if not self.name and not self.ext:
            return self.producer
        if not self.ext:
            return f'{self.producer}__{self.name}'
        return f'{self.producer}__{self.name}.{self.ext}'


RESERVED_WORKPLAN_NAMES = """\
all cache ff i input j jobs o output pages prefix wait
""".split()


@dataclasses.dataclass
class WorkPlanStep:
    name: str
    inputs: list = dataclasses.field(default_factory=list)
    outputs: list = dataclasses.field(default_factory=list)

    def __post_init__(self):
        assert self.name.lower() not in RESERVED_WORKPLAN_NAMES, (
            f'reserved workstep name: {self.name.lower()}')


WorkPlanSteps = list[WorkPlanStep]


def create_step(
    name: str,
    inputs: list['Input'] = None,
    output: tuple[str] = None,
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
    inputs = [] if not inputs else inputs
    output = [] if not output else output
    if not utila.iterable(inputs):
        inputs = [inputs]
    if not utila.iterable(output):
        output = [output]
    assert isinstance(inputs, list), f'{type(inputs)} {inputs}'
    for index, item in enumerate(inputs):
        assert isinstance(item, Input), f'{index} {item}'
    msg = f'{type(output)} {output}'
    assert isinstance(output, (tuple, list)), msg
    return utila.WorkPlanStep(name, inputs, output)
