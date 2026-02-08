# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utilo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSION = '2.33.7'
PROCESS = 'foldme'
WORKPLAN = [
    utilo.create_step(
        'directory_input',
        inputs=[
            utilo.Directory('iamadirectory'),
        ],
        output=('message',),
    ),
    utilo.create_step(
        'custom_output',
        inputs=[
            utilo.Directory('iamadirectory'),
        ],
        output=(utilo.File('helm/iamsounique', ext='txt'),),
    ),
    utilo.create_step(
        'different_datatype',
        inputs=[
            utilo.Directory('iamadirectory'),
        ],
        output=[
            utilo.File('schelm/*', ext='???'),
        ],
    ),
]


def main(**kwargs):
    config = utilo.FeaturePackConfig(
        description='This is a second feature playground.',
        multiprocessed=False,
        name=PROCESS,
        pages=True,
        singleinput=True,
        configflag=True,
        before=before_global,
        after=after_global,
        version=VERSION,
        **kwargs,
    )
    utilo.featurepack(
        config=config,
        featurepackage='foldme.features',
        root=ROOT,
        workplan=WORKPLAN,
    )


def before_global():
    pass


def after_global():
    pass
