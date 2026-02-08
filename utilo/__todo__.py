# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""T0D0-List
=========

The T0D0-List aims to use code to describe t0d0s and make them more
important.

Hint: This special module name ensures that the code is loaded very
early and we can this use even in `utila` package.
"""

import contextlib


class todo(contextlib.ContextDecorator):  # pylint:disable=C0103
    """ContextManager and Decorator to mark code areas which must be
    replaced or refactored before upgrading the requirements. This is
    even harder than a `refactor/docu` mark.
    """

    def __init__(
        self,
        version: str = None,
        major=None,
        minor=None,
        patch=None,
        description='todo',
    ):
        if version is None:
            import utilo  # pylint:disable=import-outside-toplevel
            version = utilo.__version__
        self.major = major
        self.minor = minor
        self.patch = patch
        self.description = description
        major, minor, patch = [int(item) for item in version.split('.')]
        msg = f'{self.description}: {self.major}.{self.minor}.{self.patch}'
        assert major <= self.major, msg
        if self.minor is not None and major == self.major:
            assert minor < self.minor, msg
        if self.patch is not None and minor == self.minor:
            assert patch < self.patch, msg

    def __enter__(self, major=1, minor=1, patch=None):
        yield

    def __exit__(self, *exc_info):
        pass


class refactor(todo):  # pylint:disable=C0103

    def __init__(
        self,
        version=None,
        major=None,
        minor=None,
        patch=None,
        description='time to refactor',
    ):
        super().__init__(
            version=version,
            major=major,
            minor=minor,
            patch=patch,
            description=description,
        )


class docu(todo):  # pylint:disable=C0103

    def __init__(
        self,
        version=None,
        major=None,
        minor=None,
        patch=None,
        description='extend documentation',
    ):
        super().__init__(
            version=version,
            major=major,
            minor=minor,
            patch=patch,
            description=description,
        )
