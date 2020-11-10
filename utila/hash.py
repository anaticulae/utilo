# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hashlib


def freehash(data: bytes, digits: int = 16) -> str:
    """Hash data to ease using.

    Hint: Use this for non secure approaches only.

    >>> freehash(b'this is data', digits=10)
    '2635759800462057793e'
    >>> freehash('this is string data', digits=5)
    '89299ad12d'
    >>> freehash(13371337, digits=20)
    'c4352ad929a1a77871951c66835d0b3975df24d8'
    """
    if not isinstance(data, (bytes, str)):
        data = str(data)
    if isinstance(data, str):
        # convert to byte
        data = data.encode('utf8', errors='ignore')
    hashed = hashlib.blake2b(data, digest_size=digits)
    result = hashed.hexdigest()
    return result
