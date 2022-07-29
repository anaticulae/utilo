# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila
import utila.feature.processor

PIPELINE = """\
import utila.feature.processor
import concurrent.futures

def todo(pipeline):
    print('hello')
    print(pipeline.run(sum, 20, 30))
    print(pipeline.run(sum, 20, 30))
    print(pipeline.run(sum, 20, 30))
    print(pipeline.run(sum, 20, 30))

if __name__ == "__main__":
    pipe = utila.feature.processor.Pipeline()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        pool.submit(todo, pipe)
"""


def test_pipeline(testdir):
    """Ensure to pickle pipeline object."""
    path = testdir.tmpdir.join('run.py')
    utila.file_create(path, PIPELINE)
    utila.log(utila.run(f'python {path}'))
