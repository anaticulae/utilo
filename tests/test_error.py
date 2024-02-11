#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from pytest import raises

from utila import CANCELLED_BY_USER
from utila import FAILURE
from utila import handle_error
from utila import saveme


def test_invoking_exception():

    @saveme
    def function_with_exception():
        raise Exception()

    with raises(SystemExit) as exception:
        function_with_exception()

    assert exception.value.code == FAILURE


def test_invoking_exception_with_argument():
    """Check passing decorator argument"""

    @saveme(systemexit=True)
    def function_with_exception():
        raise Exception()

    with raises(SystemExit) as exception:
        function_with_exception()

    assert exception.value.code == FAILURE


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


def test_invoking_exception_without_system_exit():

    @saveme(systemexit=False)
    def function_with_exception():
        raise Exception()

    returncode = function_with_exception()

    assert returncode == FAILURE

    @saveme(systemexit=False)
    def no_exception():
        return 'Hallo'

    returncode = no_exception()

    assert returncode == 'Hallo'


def test_error_handle_error():
    """Catch raised error and return specified return code `37`"""
    with raises(SystemExit) as exception:
        with handle_error(ValueError, code=37):
            raise ValueError()

    assert exception.value.code == 37
