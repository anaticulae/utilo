# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila.feature.pack


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

    result = utila.feature.pack.determine_todo(args, flags)
    assert result == [], str(result)
