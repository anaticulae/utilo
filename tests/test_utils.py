# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest

import utila


def test_roundme():
    rounded = utila.roundme(2.3333)
    assert rounded == 2.33


def test_flatten():
    todo = [
        [10],
        [1, 2],
        [1, 2, 3, 4],
    ]
    flat = utila.flatten(todo)
    assert len(flat) == 7, str(flat)


def test_chdir(testdir):
    """Test to change working directory given path. Ensure that
    exceptions are handled correctly."""
    root = str(testdir)

    folder = os.path.join(root, 'folder')
    os.makedirs(folder)
    assert os.path.exists(folder)

    assert root == str(os.getcwd())

    with utila.chdir(folder):
        # check to change current working directory
        assert str(os.getcwd()) == folder

    # check going back to preview working directory
    assert str(os.getcwd()) == root

    with pytest.raises(ValueError):
        with utila.chdir(folder):
            # check to change current working directory
            assert str(os.getcwd()) == folder
            raise ValueError()

    # check going back to preview working directory
    assert str(os.getcwd()) == root
