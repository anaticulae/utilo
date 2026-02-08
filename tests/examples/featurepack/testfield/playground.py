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
VERSION = '1.33.7'
PROCESS = 'testfield'
WORKPLAN = [
    utilo.create_step(
        'household',
        inputs=[
            utilo.File('infile'),
            utilo.Value('char_margin', float, defaultvar=2.0, minimum=0.1),
            utilo.Bool('sync'),
        ],
        output=('first',),
    ),
    utilo.create_step(
        'binary',
        output=(('binary', 'hex'),),
    ),
    utilo.create_step(
        'multiple',
        output=[
            ('*_info', 'yaml'),
            ('*_binary', 'hex'),
        ],
    ),
    utilo.create_step(
        'datatype',
        output=[
            ('selected', '???'),
        ],
    ),
    utilo.create_step(
        'datatype_multi',
        output=[
            ('*', '???'),
        ],
    ),
    utilo.create_step(
        'hashed',
        output=[
            ('{FILEHASHS}', 'bin'),
        ],
    ),
    utilo.create_step(
        'hashed_multi',
        output=[
            ('figures/{FILEHASH_1}', 'yaml'),
            ('figures/{FILEHASHS}', '???'),
        ],
    ),
    utilo.create_step(
        'hashed_list_ext',
        output=[
            ('figures/{FILEHASHS}', '???'),
        ],
    ),
]


def main(**kwargs):
    config = utilo.FeaturePackConfig(
        description='This is a default feature pack to increase test coverage',
        multiprocessed=True,
        name=PROCESS,
        pages=True,
        singleinput=True,
        configflag=True,
        version=VERSION,
        **kwargs,
    )
    utilo.featurepack(
        config=config,
        featurepackage='testfield.features',
        root=ROOT,
        workplan=WORKPLAN,
    )
