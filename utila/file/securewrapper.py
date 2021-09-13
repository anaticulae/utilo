# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import shutil

import utila

OPEN = open
HEADER_STR = br'%ENC-STR'
HEADER_BIN = br'%ENC-BIN'


class SecureFile(contextlib.ContextDecorator):

    def __init__(
        self,
        path,
        binary: bool = False,
        append: bool = False,
        read: bool = False,
    ):
        self.path = path
        self.content = b'' if binary else ''
        self.readme = read
        self.append = append
        self.binary = binary  # not necessary

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.readme:
            return
        if self.append:
            mode = 'rb' if self.binary else 'r'
            with open(self.path, mode=mode) as fp:
                content = fp.read()
            self.content = content + self.content
        # write cached content
        encrypted = utila.encrypt(self.content)
        content = HEADER_BIN if self.binary else HEADER_STR
        content += encrypted
        with OPEN(self.path, mode='bw') as fp:
            fp.write(content)

    def write(self, content):
        self.content += content

    def read(self, size: int = -1):
        with OPEN(self.path, mode='br') as fp:
            content = fp.read()
        header = content[0:len(HEADER_STR)]
        string = header == HEADER_STR
        byte = header == HEADER_BIN
        # if string or byte, strip header and decrypt.
        # if no header is given, return file content
        if string or byte:
            # strip header
            content = content[len(header):]
            # plain text
            content = utila.decrypt(content, string=string)
        elif not self.binary:
            content: str = bytes.decode(content, 'utf8')
        if size != -1:
            if isinstance(size, tuple):
                return content[size[0]:size[0]]
            return content[0:size]
        return content


@contextlib.contextmanager
def open(  # pylint:disable=redefined-builtin
    path,
    mode=None,
    newline=None,
    encoding='utf8',
    private: bool = False,
):
    binary = 'b' in mode
    write = 'w' in mode
    append = 'a' in mode
    read = 'r' in mode
    if not private and (write or append):
        if binary:
            yield OPEN(path, mode=mode)
        else:
            yield OPEN(path, mode=mode, newline=newline, encoding=encoding)
        return
    with SecureFile(path, binary, append, read) as secure:
        yield secure


COPY = shutil.copy


def copy(src, dst, private: bool = False):
    if not private:
        COPY(src, dst)
        return
    header = utila.file_read_binary(src)
    header = header[0:len(utila.file.securewrapper.HEADER_STR)]
    if header == utila.file.securewrapper.HEADER_STR:
        content = utila.file_read(src, private=True)
        utila.file_replace(dst, content, private=True)
        return
    if header == utila.file.securewrapper.HEADER_BIN:
        content = utila.file_read_binary(src, private=True)
        utila.file_replace_binary(dst, content, private=True)
        return
    try:
        content = utila.file_read(src, private=False)
        utila.file_replace(dst, content, private=True)
    except UnicodeDecodeError:
        content = utila.file_read_binary(src, private=False)
        utila.file_replace_binary(dst, content, private=True)
