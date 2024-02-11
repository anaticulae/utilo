# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila
import utila.file.loader


def test_file_find(tmpdir):
    utila.file_create(tmpdir.join('debug'))
    detected = utila.file.loader.file_find(
        tmpdir,
        fnames='debug',
    )
    assert detected
