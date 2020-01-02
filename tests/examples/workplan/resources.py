# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import utila

PDF = utila.Pattern('*', 'pdf')

CHAR_MARGIN = utila.Value('char_margin', float, defaultvar=2.0, minimum=0.1)
LINE_OVERLAP = utila.Value('line_overlap', float, defaultvar=0.5, minimum=0.1)
LINE_MARGIN = utila.Value('line_margin', float, defaultvar=0.5, minimum=0.1)
WORD_MARGIN = utila.Value('word_margin', float, defaultvar=0.1, minimum=0.1)
BOXES_FLOW = utila.Value('boxes_flow', float, defaultvar=0.5, minimum=0.1)

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
    utila.create_step(
        'annotation',
        inputs=PDF_INPUT,
        output=('annotation',),
    ),
    utila.create_step(
        'border',
        inputs=PDF_INPUT,
        output=(
            'pages',
            'boundingboxes',
        ),
    ),
    utila.create_step(
        'boxes',
        inputs=PDF_INPUT,
        output=(
            'boxes',
            'horizontal',
        ),
    ),
    utila.create_step(
        'fonts',
        inputs=CONFIG_INPUTS,
        output=(
            'header',
            'content',
        ),
    ),
    utila.create_step(
        'text',
        inputs=CONFIG_INPUTS,
        output=(
            'text',
            'positions',
        ),
    ),
    utila.create_step(
        'toc',
        inputs=PDF_INPUT,
        output=('toc',),
    ),
]
