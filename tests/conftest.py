# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest

from tests.fixtures.line import lines  # pylint:disable=W0611
from tests.fixtures.line import thousand_lines  # pylint:disable=W0611

pytest_plugins = ['pytester', 'xdist']  # pylint: disable=invalid-name


@pytest.fixture(scope="session", autouse=True)
def git_identity_for_tests():
    os.environ["GIT_AUTHOR_NAME"] = "Super Mario"
    os.environ["GIT_AUTHOR_EMAIL"] = "test@example.com"
    os.environ["GIT_COMMITTER_NAME"] = "Super Mario"
    os.environ["GIT_COMMITTER_EMAIL"] = "test@example.com"


@pytest.fixture
def mp(monkeypatch):
    return monkeypatch


@pytest.fixture
def td(testdir):
    return testdir
