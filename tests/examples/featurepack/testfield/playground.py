# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSION = '1.33.7'
PROCESS = 'testfield'
WORKPLAN = [
    utila.create_step(
        'household',
        inputs=[
            utila.File('infile'),
            utila.Value('char_margin', float, defaultvar=2.0, minimum=0.1),
            utila.Bool('sync'),
        ],
        output=('first',),
    ),
    utila.create_step(
        'binary',
        output=(('binary', 'hex'),),
    ),
    utila.create_step(
        'multiple',
        output=[
            ('*_info', 'yaml'),
            ('*_binary', 'hex'),
        ],
    ),
    utila.create_step(
        'datatype',
        output=[
            ('selected', '???'),
        ],
    ),
    utila.create_step(
        'datatype_multi',
        output=[
            ('*', '???'),
        ],
    ),
    utila.create_step(
        'hashed',
        output=[
            ('{FILEHASHS}', 'bin'),
        ],
    ),
    utila.create_step(
        'hashed_multi',
        output=[
            ('figures/{FILEHASH_1}', 'yaml'),
            ('figures/{FILEHASHS}', '???'),
        ],
    ),
    utila.create_step(
        'hashed_list_ext',
        output=[
            ('figures/{FILEHASHS}', '???'),
        ],
    ),
]


def main(**kwargs):
    config = utila.FeaturePackConfig(
        description='This is a default feature pack to increase test coverage',
        multiprocessed=True,
        name=PROCESS,
        pages=True,
        singleinput=True,
        configflag=True,
        version=VERSION,
        **kwargs,
    )
    utila.featurepack(
        config=config,
        featurepackage='testfield.features',
        root=ROOT,
        workplan=WORKPLAN,
    )
