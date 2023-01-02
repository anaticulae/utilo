# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import subprocess  # nosec

import utila


def run(argv: list) -> int:
    runnable = utila.file_name(argv[0])
    argv[0] = runnable
    outpath = f'{runnable}.bin'
    argv.remove('--cprofile')
    usercmd = ' '.join(argv)
    cmd = f'python -m cProfile -o {outpath} -m {usercmd}'
    utila.log(cmd)
    completed = subprocess.run(cmd, check=False)  # pylint:disable=subprocess-run-check #nosec
    return completed.returncode
