# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import utilo

PDF = utilo.Pattern('*', 'pdf')

CHAR_MARGIN = utilo.Value('char_margin', float, defaultvar=2.0, minimum=0.1)
LINE_OVERLAP = utilo.Value('line_overlap', float, defaultvar=0.5, minimum=0.1)
LINE_MARGIN = utilo.Value('line_margin', float, defaultvar=0.5, minimum=0.1)
WORD_MARGIN = utilo.Value('word_margin', float, defaultvar=0.1, minimum=0.1)
BOXES_FLOW = utilo.Value('boxes_flow', float, defaultvar=0.5, minimum=0.1)

PDF_INPUT = [PDF]

CONFIG_INPUTS = [
    PDF,
    BOXES_FLOW,
    CHAR_MARGIN,
    LINE_MARGIN,
    LINE_OVERLAP,
    WORD_MARGIN,
]

ROOT = 'rawmaker'
WORKPLAN = [
    utilo.create_step(
        'annotation',
        inputs=PDF_INPUT,
        output=('annotation',),
    ),
    utilo.create_step(
        'border',
        inputs=PDF_INPUT,
        output=(
            'pages',
            'boundingboxes',
        ),
    ),
    utilo.create_step(
        'boxes',
        inputs=PDF_INPUT,
        output=(
            'boxes',
            'horizontal',
        ),
    ),
    utilo.create_step(
        'fonts',
        inputs=CONFIG_INPUTS,
        output=(
            'header',
            'content',
        ),
    ),
    utilo.create_step(
        'text',
        inputs=CONFIG_INPUTS,
        output=(
            'text',
            'positions',
        ),
    ),
    utilo.create_step(
        'toc',
        inputs=PDF_INPUT,
        output=('toc',),
    ),
]
