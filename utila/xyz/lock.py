# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse

import utila

LOCK = 'utila_lock'
UNLOCK = 'utila_unlock'


def main():
    parser = argparse.ArgumentParser(prog=LOCK)
    args = parser.parse_args()  # pylint:disable=W0612
    cwd = utila.cwdget()
    utila.exists_assert(cwd)
    utila.log(cwd)
    # ask user to continue
    utila.wait()
    utila.directory_lock(cwd)
    utila.exitx(returncode=utila.SUCCESS)


def unlock():
    parser = argparse.ArgumentParser(prog=UNLOCK)
    args = parser.parse_args()  # pylint:disable=W0612
    cwd = utila.cwdget()
    utila.exists_assert(cwd)
    utila.log(cwd)
    # ask user to continue
    utila.wait()
    utila.directory_unlock(cwd)
    utila.exitx(returncode=utila.SUCCESS)
