# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSION = '2.33.7'
PROCESS = 'foldme'
WORKPLAN = [
    utila.create_step(
        'directory_input',
        inputs=[
            utila.Directory('iamadirectory'),
        ],
        output=('message',),
    ),
    utila.create_step(
        'custom_output',
        inputs=[
            utila.Directory('iamadirectory'),
        ],
        output=(utila.File('helm/iamsounique', ext='txt'),),
    ),
]


def main(**kwargs):
    config = utila.FeaturePackConfig(
        description='This is a second feature playground.',
        multiprocessed=False,
        name=PROCESS,
        pages=True,
        singleinput=True,
        configflag=True,
        version=VERSION,
        **kwargs,
    )
    utila.featurepack(
        config=config,
        featurepackage='foldme.features',
        root=ROOT,
        workplan=WORKPLAN,
    )
