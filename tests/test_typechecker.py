# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
from pytest import raises

from utila import checkdatatype


@checkdatatype
def three_args(first: str, second: int, third: str):
    pass


@checkdatatype
def no_datatype(oneelement):
    pass


def test_typechecker_checkdatatype():
    three_args('Hello', 10, 'Final')


def test_typechecker_checkdatatype_error():
    with raises(ValueError):
        three_args(0, 0, 0)


def test_typechecker_checkdatatype_non_datatypes():
    no_datatype('10')
    no_datatype('Hello')
    no_datatype(10)
    no_datatype(1.0)
