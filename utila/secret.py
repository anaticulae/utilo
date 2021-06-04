# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import os

import utila
import utila.logger

try:
    # TODO: DO NOT RELASE BEFORE UPGRADE
    # TODO: REPLACE WITH UPTODATE LIB
    from Crypto.Cipher import AES
except ModuleNotFoundError:
    utila.logger.error('could not use Crypto')
    AES = None

BLOCKSIZE = 32
# TODO: REPLACE WITH WORKING ONE

# UTILA_USER_PASSWORD


def encrypt(plaintext: bytes) -> bytes:
    r"""Convert plain text to cipher text."""
    if isinstance(plaintext, str):
        plaintext = plaintext.encode(
            encoding='utf8',
            errors='xmlcharrefreplace',
        )
    if AES:
        plaintext = create_block(plaintext)
        ciphertext = aes().encrypt(plaintext)
    else:
        ciphertext = _encrypt_toy(plaintext)
    return ciphertext


def decrypt(ciphertext: bytes, string: bool = False) -> bytes:
    """Convert cipher text to plain text."""
    if AES:
        plaintext = aes().decrypt(ciphertext)
        plaintext = remove_block(plaintext)
    else:
        plaintext = _decrypt_toy(ciphertext)
    if string:
        plaintext: str = plaintext.decode(encoding='utf8')
    return plaintext


def password() -> str:
    result = os.environ.get('UTILA_USER_PASSWORD', 'NOPASSWORD')
    return result


def aes():
    # normalize password
    pwd = password()
    pwd = utila.secure_hash(pwd, digits=32)
    pwd: bytes = pwd.encode('utf8')
    # TODO: VERIFY PROS AND CONS OF MODE
    result = AES.new(pwd, AES.MODE_ECB)
    return result


def create_block(content: bytes):
    """\
    >>> create_block(b'abc' * 15)
    b'abcabcabcabcabcabcabcabcabcabcabcabcabcabcabc                   '
    """
    if len(content) % BLOCKSIZE == 0:
        return content
    missing = math.ceil(len(content) / BLOCKSIZE) * BLOCKSIZE - len(content)
    content = content + b' ' * missing
    return content


def remove_block(content: bytes):
    stripped = content.rstrip()
    if content[len(stripped):len(stripped) + 1] == b'\n':
        # valid file ends with newline
        stripped = content[0:len(stripped) + 1]
    return stripped


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
