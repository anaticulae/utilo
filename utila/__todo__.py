# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""T0D0-List
=========

The T0D0-List aims to use code to descripe t0d0s and make them more
important.

Hint: This special module name ensures that the code is loaded very
early and we can this use even in `utila` package.
"""

import contextlib


class todo(contextlib.ContextDecorator):  # pylint:disable=C0103
    """ContextManager and Decorator to mark code areas which must be
    replaced or refactored before upgrading the requirements. This is
    even harder than a `todo` mark.
    """

    def __init__(
            self,
            major=1,
            minor=1,
            patch=None,
            description='todo',
    ):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.description = description

        import utila
        major, minor, patch = [
            int(item) for item in utila.__version__.split('.')
        ]
        msg = f'{self.description}: {self.major}.{self.minor}.{self.patch}'
        assert major <= self.major, msg
        if minor is not None and major == self.major:
            assert minor < self.minor, msg
        if patch is not None and minor == self.minor:
            assert patch < self.patch, msg

    def __enter__(self, major=1, minor=1, patch=None):
        yield

    def __exit__(self, *exc_info):
        pass


class refactor(todo):  # pylint:disable=C0103

    def __init__(
            self,
            major=1,
            minor=1,
            patch=None,
            description='time to refactor',
    ):
        super().__init__(
            major=major,
            minor=minor,
            patch=patch,
            description=description,
        )


class docu(todo):  # pylint:disable=C0103

    def __init__(
            self,
            major=1,
            minor=1,
            patch=None,
            description='extend documentation',
    ):
        super().__init__(
            major=major,
            minor=minor,
            patch=patch,
            description=description,
        )
