# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila

NO_YAML = """
PDFInfo(pages=51, generator=<PDFGenerator.UNDEFINED: 1>, \
version=PDFVersion(major=1, minor=4), meta={'author': 'Innendienst',
'creationdate': "D:20160501184537+02'00'", 'creator': 'PDF24 Creator',
'moddate': "D:20160501184537+02'00'", 'producer': 'GPL Ghostscript
9.14', 'title': 'Microsoft Word - bt_235251_laas_ilja'})
"""


def test_yaml_from_error():
    with pytest.raises(ValueError, match='no valid yaml input'):
        utila.yaml_from_raw_or_path(NO_YAML)
