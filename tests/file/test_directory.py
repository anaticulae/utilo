# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def test_directory_lock(tmpdir):
    write = tmpdir.mkdir('sub').join('hello.txt')
    write.write('content')
    utila.directory_lock(tmpdir)
    assert utila.file_islocked(write)
    utila.directory_unlock(tmpdir)
    assert not utila.file_islocked(write)
