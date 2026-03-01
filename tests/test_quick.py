# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import setuptools._distutils.core

import utilo


def test_quick_install(td, mp):
    root = str(td.tmpdir)
    project = 'no_project'
    cmd = f'baw init {project} "nice example"'
    utilo.run(
        cmd,
        cwd=root,
    )
    setup = td.tmpdir.join('setup.py')

    def no_install(**attrs):  # pylint:disable=W0613
        pass

    # TODO: ENABLE LATER
    # with mp.context() as context:
    #     context.setattr(setuptools._distutils.core, 'setup', no_install)  # pylint:disable=W0212
    #     utilo.install(root=setup)
