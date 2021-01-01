# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
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
    config = utila.FeaturePackConfig(
        description='Test the error hook feature',
        errorhook=errorhook,
        multiprocessed=True,
        name=PROCESS,
        pages=True,
        singleinput=True,
        version=VERSION,
        before=before,
        after=after,
    )
    utila.featurepack(
        config=config,
        featurepackage='withexception.features',
        root=ROOT,
        workplan=WORKPLAN,
    )


def errorhook(name, exception):  # pylint:disable=W0613
    pass


def before():
    pass


def after():
    pass
