# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import tests.examples.workplan.groupme
import utila.feature.description


def test_feature_description_groupme():
    workplan = tests.examples.workplan.groupme.WORKPLAN
    name = tests.examples.workplan.groupme.ROOT
    description = ''
    result = utila.feature.description.prepare_description(
        name,
        description,
        workplan,
    )

    first = """\
//chapter
+rawmaker__text_text.yaml
>groupme__chapter_charls.yaml
"""

    fourth = """\
//footer
+groupme__pagenumbers_pagenumbers.yaml   +rawmaker__border_pages.yaml      +rawmaker__boxes_horizontal.yaml
+rawmaker__text_positions.yaml    +rawmaker__text_text.yaml
>groupme__footer_result.yaml
"""
    assert first in result, result
    assert fourth in result, result
