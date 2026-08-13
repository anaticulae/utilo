# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hashlib
import math


def freehash(data: bytes | str, digits: int = 16, returns=str) -> str | int:
    """Hash data to ease using.

    Hint: Use this for non secure approaches only.

    >>> freehash(b'this is data', digits=10)
    '492cb96eda'
    >>> freehash('this is string data', digits=5)
    '6eb828'
    >>> freehash(13371337, digits=20)
    '1d6894801cdd2e11e98f'
    >>> freehash(13371337, digits=20, returns=int)
    13689480123324114985
    """
    if not isinstance(data, (bytes, str)):
        data = str(data)
    if isinstance(data, str):
        # convert to byte
        data: bytes = data.encode('utf8', errors='ignore')
    # hexdigits produces two chars for one digit?
    digits = math.ceil(digits / 2)
    hashed = hashlib.blake2b(data, digest_size=digits)
    result = hashed.hexdigest()
    if returns == int:
        result = (c if c.isdigit() else str(ord(c) - ord('a')) for c in result)
        result: int = int(''.join(result))
    return result


def secure_hash(data: bytes, digits: int = 256, salt: str = None) -> str:  # pylint:disable=W0613
    # TODO: INTRODUCE SECURE ONE
    return freehash(data, digits=digits)
