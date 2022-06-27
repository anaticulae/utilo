# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import os

import utila


def main():
    parser = argparse.ArgumentParser(prog='utila_lock')
    args = parser.parse_args()  # pylint:disable=W0612
    cwd = os.getcwd()
    utila.exists_assert(cwd)
    utila.log(cwd)
    # ask user to continue
    utila.wait()
    utila.directory_lock(cwd)
    return utila.SUCCESS
