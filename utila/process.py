# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import concurrent

import utila


def run_parallel(items, cwd=None, worker: int = 8) -> int:
    """Run `items` as list of commands in parallel."""
    ret = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker) as executor:
        todo = {executor.submit(utila.run, cmd, cwd): cmd for cmd in items}
        for future in concurrent.futures.as_completed(todo):
            current = todo[future]
            try:
                data = future.result()
                assert data.returncode == utila.SUCCESS, data
            except Exception as exc:  # pylint:disable=broad-except
                utila.error(f'{current} generated an exception: {exc}')
                ret += 1
    return ret
