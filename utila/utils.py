#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

SUCCESS = 0
FAILURE = 1

TMP = '.tmp'
UTF8 = 'utf8'
NEWLINE = '\n'


def forward_slash(content: str):
    """Replace every backward slash \\ with an forward slash /

    Args:
        content(str): content with backslashs
    Returns:
        content without backslashs
    """
    content = str(content).replace(r'\\', '/').replace('\\', '/')
    return content
