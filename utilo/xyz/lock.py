# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse

import utilo

LOCK = 'utilo_lock'
UNLOCK = 'utilo_unlock'


def main():
    parser = argparse.ArgumentParser(prog=LOCK)
    args = parser.parse_args()  # pylint:disable=W0612
    cwd = utilo.cwdget()
    utilo.exists_assert(cwd)
    utilo.log(cwd)
    # ask user to continue
    utilo.wait()
    utilo.directory_lock(cwd)
    utilo.exitx(returncode=utilo.SUCCESS)


def unlock():
    parser = argparse.ArgumentParser(prog=UNLOCK)
    args = parser.parse_args()  # pylint:disable=W0612
    cwd = utilo.cwdget()
    utilo.exists_assert(cwd)
    utilo.log(cwd)
    # ask user to continue
    utilo.wait()
    utilo.directory_unlock(cwd)
    utilo.exitx(returncode=utilo.SUCCESS)
