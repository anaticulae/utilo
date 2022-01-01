# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila

try:
    import utilasafe
except ModuleNotFoundError:
    utila.error('could not use utilasafe')
    utilasafe = None  # pylint:disable=C0103


def encrypt(plaintext: bytes) -> bytes:
    r"""Convert plain text to cipher text."""
    if isinstance(plaintext, str):
        plaintext = plaintext.encode(
            encoding='utf8',
            errors='xmlcharrefreplace',
        )
    if utilasafe:
        ciphertext = utilasafe.encrypt_password(plaintext)
    else:
        ciphertext = _encrypt_toy(plaintext)
    return ciphertext


def decrypt(ciphertext: bytes, string: bool = False) -> bytes:
    """Convert cipher text to plain text."""
    if utilasafe:
        plaintext = utilasafe.decrypt_password(ciphertext)
    else:
        plaintext = _decrypt_toy(ciphertext)
    if string:
        plaintext: str = plaintext.decode(encoding='utf8')
    return plaintext


def _encrypt_toy(plaintext: bytes) -> bytes:
    r"""\
    >>> _encrypt_toy(b'hello')
    b'\xea\xe7\xee\xee\xf1'
    >>> _decrypt_toy(_encrypt_toy(b'hello'))
    b'hello'
    """
    key = hash(password()) // 256
    ciphertext = [(item + key) % 256 for item in plaintext]
    ciphertext = bytes(ciphertext)
    return ciphertext


def _decrypt_toy(ciphertext: bytes) -> bytes:
    key = hash(password()) // 256
    plaintext = ([(item - key) % 256 for item in ciphertext])
    plaintext = bytes(plaintext)
    return plaintext


def password() -> str:
    result = os.environ.get('UTILASAFE_USER_PASSWORD', 'NOPASSWORD')
    return result
