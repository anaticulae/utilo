# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections
import os

import pytest

import utilo


def test_roundme():
    rounded = utilo.roundme(2.3333)
    assert rounded == 2.33


def test_flat():
    todo = [
        [10],
        [1, 2],
        [1, 2, 3, 4],
    ]
    flat = utilo.flat(todo)
    assert len(flat) == 7, str(flat)


def test_select_type():

    class A:  # pylint:disable=C0103
        pass

    class B(A):  # pylint:disable=C0103
        pass

    todo = [A(), B(), A()]
    assert len(utilo.select_type(todo, A)) == 3
    assert len(utilo.select_type(todo, B)) == 1


def test_chdir(td):
    """Test to change working directory given path. Ensure that
    exceptions are handled correctly."""
    root = str(td)

    folder = os.path.join(root, 'folder')
    os.makedirs(folder)
    assert os.path.exists(folder)

    assert root == utilo.cwdget()

    with utilo.chdir(folder):
        # check to change current working directory
        assert utilo.cwdget() == folder

    # check going back to preview working directory
    assert utilo.cwdget() == root

    with pytest.raises(ValueError):
        with utilo.chdir(folder):
            # check to change current working directory
            assert utilo.cwdget() == folder
            raise ValueError()

    # check going back to preview working directory
    assert utilo.cwdget() == root


def test_chdir_to_filepath(td):
    """Test to change to a file location with contextmanager."""
    root = str(td)

    filepath = os.path.join(root, 'hello')
    utilo.file_create(filepath)

    assert os.path.exists(filepath)
    with pytest.raises(AssertionError):
        with utilo.chdir(filepath):
            pass


def test_unset_env(mp):
    with mp.context() as context:
        context.setattr(os, 'environ', {})
        os.environ['abc'] = '10'
        with utilo.unset_env('abc'):
            assert not 'abc' in os.environ
        assert 'abc' in os.environ
        del os.environ['abc']


def test_unset_env_keyerror(mp):
    with mp.context() as context:
        context.setattr(os, 'environ', {})
        with pytest.raises(KeyError):
            with utilo.unset_env('abc', skip=False):
                pass


def test_selbstwirksamkeit_all():
    Driver = collections.namedtuple('Driver', 'first second third')
    data = Driver(10, 15, 20)

    @utilo.selbstwirksamkeit
    def method(first, second):
        return first + second

    # tuple access
    result = method(data)  # pylint:disable=E1120
    assert result == 25

    # dict access
    data = dict(first=10, second=15, third=20)  # pylint:disable=R0204
    result = method(data)  # pylint:disable=E1120
    assert result == 25


def test_selbstwirksamkeit_missing():
    Driver = collections.namedtuple('Driver', 'first second third')
    data = Driver(10, 15, 20)

    @utilo.selbstwirksamkeit
    def method(first, missing):  # pylint:disable=W0613
        return first

    with pytest.raises(AttributeError, match='is not provided by data'):
        method(data)  # pylint:disable=E1120


def test_selbstwirksamkeit_replace():
    Driver = collections.namedtuple('Driver', 'first second third')
    data = Driver(10, 15, 20)

    @utilo.selbstwirksamkeit(usenone=True)
    def method(first, missing):
        assert missing is None
        return first

    assert method(data) == 10  # pylint:disable=E1120
