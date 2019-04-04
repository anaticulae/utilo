#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from pytest import raises
from utila import saveme
from utila.error import CANCELLED_BY_USER


def test_invoking_execption():

    @saveme
    def function_with_exception():
        raise Exception()

    with raises(SystemExit) as exception:
        function_with_exception()

    assert exception.value.code == 1


def test_canceling_by_user():

    @saveme
    def keyboard_interrupt():
        raise KeyboardInterrupt

    with raises(SystemExit) as exception:
        keyboard_interrupt()

    assert exception.value.code == CANCELLED_BY_USER


def test_invoking_empty():

    @saveme
    def function():
        return 2

    with raises(SystemExit) as exception:
        function()
    assert exception.value.code == 2
