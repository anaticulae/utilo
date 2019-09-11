# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSION = '1.33.7'
PROCESS = 'brokenworker'
WORKPLAN = [
    utila.create_step(
        'brokenworker',
        inputs=[utila.File('inputs')],
        output=('first', 'second'),
    ),
]


def main():
    utila.featurepack(
        description='Test the error hook feature',
        errorhook=errorhook,
        featurepackage='withexception.features',
        multiprocessed=True,
        name=PROCESS,
        pages=True,
        root=ROOT,
        singleinput=True,
        version=VERSION,
        workplan=WORKPLAN,
    )


def errorhook(name, exception):  # pylint:disable=W0613
    pass
