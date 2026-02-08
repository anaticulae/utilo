# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from utilo import ResultFile
from utilo import WorkPlanStep
from utilo import create_step as step

ROOT = 'groupme'

WORKPLAN = [
    step(
        'chapter',
        inputs=[
            ResultFile(producer='rawmaker', name='text_text'),
        ],
        output=('charls',),
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
        output=('result',),
    )
]

PLAN_WITH_PATH = [
    WorkPlanStep(
        name='chapter',
        inputs=['C:\\restruct\\rawmaker__text_text.yaml)'],
        outputs=['C:\\restruct\\groupme__chapter_chapter.yaml'],
    ),
    WorkPlanStep(
        name='toc',
        inputs=['C:\\restruct\\rawmaker__text_text.yaml)'],
        outputs=['C:\\restruct\\groupme__toc_toc.yaml'],
    ),
    WorkPlanStep(
        name='pagenumbers',
        inputs=[
            'C:\\restruct\\rawmaker__text_text.yaml',
            'C:\\restruct\\rawmaker__text_positions.yaml'
        ],
        outputs=['C:\\restruct\\groupme__pagenumbers_pagenumbers.yaml'],
    ),
    WorkPlanStep(
        name='footer',
        inputs=[
            'C:\\restruct\\rawmaker__text_text.yaml',
            'C:\\restruct\\rawmaker__text_positions.yaml',
            'C:\\restruct\\rawmaker__boxes_horizontal.yaml',
            'C:\\restruct\\rawmaker__border_pages.yaml',
            'C:\\restruct\\groupme__pagenumbers_pagenumbers.yaml'
        ],
        outputs=['C:\\restruct\\groupme__footer_footer.yaml'],
    )
]
