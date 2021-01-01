# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re

import utila


def test_regex_extract_match():
    word = r'(?P<word>\w+)'
    text = 'this is helmut'
    matched = re.match(word, text)

    extracted = utila.extract_match(matched)
    assert extracted == 'this', extracted

    matched = re.finditer(word, text)
    raw = [utila.extract_match(item) for item in matched]
    assert raw == text.split()
