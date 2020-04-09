# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import tests.feature.runner


def run_foldme(
        cmd: str,
        main: dict,
        testdir,
        monkeypatch,
        capsys=None,
):
    import tests.examples.featurepack.foldme.morefeatures as exe
    result = tests.feature.runner.run_featurepack(
        cmd=cmd,
        main=main,
        testdir=testdir,
        monkeypatch=monkeypatch,
        exe=exe,
        capsys=capsys,
    )
    return result
