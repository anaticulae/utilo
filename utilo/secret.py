# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hashlib
import os

import utilosafe


def encrypt(plaintext: bytes) -> bytes:
    """Convert plain text to cipher text."""
    if isinstance(plaintext, str):
        plaintext = plaintext.encode(
            encoding='utf8',
            errors='xmlcharrefreplace',
        )
    ciphertext = utilosafe.encrypt_password(plaintext)
    return ciphertext


def decrypt(ciphertext: bytes, string: bool = False) -> bytes:
    """Convert cipher text to plain text."""
    plaintext = utilosafe.decrypt_password(ciphertext)
    if string:
        plaintext: str = plaintext.decode(encoding='utf8')
    return plaintext


def _encrypt_toy(plaintext: bytes) -> bytes:
    r"""\
    >>> _encrypt_toy(b'hello')
    b'\xae\xab\xb2\xb2\xb5'
    >>> _decrypt_toy(_encrypt_toy(b'hello'))
    b'hello'
    """
    key = int(hashlib.sha256(password().encode()).hexdigest(), 16) // 256
    ciphertext = [(item + key) % 256 for item in plaintext]
    ciphertext = bytes(ciphertext)
    return ciphertext


def _decrypt_toy(ciphertext: bytes) -> bytes:
    key = int(hashlib.sha256(password().encode()).hexdigest(), 16) // 256
    plaintext = ([(item - key) % 256 for item in ciphertext])
    plaintext = bytes(plaintext)
    return plaintext


def password() -> str:
    result = os.environ.get('UTILASAFE_USER_PASSWORD', 'NOPASSWORD')
    return result
