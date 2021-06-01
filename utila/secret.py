# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

# TODO: REPLACE WITH WORKING ONE

# UTILA_USER_PASSWORD


def password():
    return os.environ.get('UTILA_USER_PASSWORD', 'NOPASSWORD')


def encrypt(plaintext: bytes) -> bytes:
    r"""Convert plain text to cipher text.

    >>> encrypt('hello')
    b'\xea\xe7\xee\xee\xf1'
    >>> decrypt(encrypt(b'hello'), string=True)
    'hello'
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode(
            encoding='utf8',
            errors='xmlcharrefreplace',
        )
    key = hash(password()) // 256
    ciphertext = [(item + key) % 256 for item in plaintext]
    ciphertext = bytes(ciphertext)
    return ciphertext


def decrypt(ciphertext: bytes, string: bool = False) -> bytes:
    """Convert cipher text to plain text."""
    key = hash(password()) // 256
    plaintext = ([(item - key) % 256 for item in ciphertext])
    plaintext = bytes(plaintext)
    if string:
        plaintext: str = plaintext.decode(encoding='utf8')
    return plaintext
