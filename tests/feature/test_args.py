# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from utila.feature import determine_todo


def test_feature_determine_todo():
    args = {
        'input': '',
        'output': '',
        'linter': True,
        'parameter': False,
    }

    flags = [
        ('linter', 'write linter results'),
        '--parameter',
        'not_there',
    ]

    result = determine_todo(args, flags)
    assert result == [], str(result)
