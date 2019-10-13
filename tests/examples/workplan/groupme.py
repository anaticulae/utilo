# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from utila import ResultFile
from utila import create_step as step

ROOT = 'groupme'

WORKPLAN = [
    step(
        'chapter',
        inputs=[
            ResultFile(producer='rawmaker', name='text_text'),
        ],
        output=('chapter',),
    ),
    step(
        'toc',
        inputs=[
            ResultFile(producer='rawmaker', name='text_text'),
        ],
        output=('toc',),
    ),
    step(
        'pagenumbers',
        inputs=[
            ResultFile(producer='rawmaker', name='text_text'),
            ResultFile(producer='rawmaker', name='text_positions'),
        ],
        output=('pagenumbers',),
    ),
    step(
        'footer',
        inputs=[
            ResultFile(producer='rawmaker', name='text_text'),
            ResultFile(producer='rawmaker', name='text_positions'),
            ResultFile(producer='rawmaker', name='boxes_horizontal'),
            ResultFile(producer='rawmaker', name='border_pages'),
            ResultFile(producer='groupme', name='pagenumbers_pagenumbers'),
        ],
        output=('footer',),
    )
]
