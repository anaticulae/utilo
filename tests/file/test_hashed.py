# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def test_file_hash():
    hashed = utila.file_hash(__file__)
    assert hashed


def test_directory_hash():
    hashed = utila.directory_hash('.', ftype='py')
    assert hashed
