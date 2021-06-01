# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

import utila.secret

OPEN = open
HEADER_STRING = b'&&&&STRING&&&&'
HEADER_BYTES = b'&&&&BYTES&&&&&'


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
        # write cached content
        encrypted = utila.secret.encrypt(self.content)
        content = HEADER_BYTES if self.binary else HEADER_STRING
        content += encrypted
        with OPEN(self.path, mode='bw') as fp:
            fp.write(content)

    def write(self, content):
        self.content += content

    def read(self):
        with OPEN(self.path, mode='br') as fp:
            content = fp.read()
        header = content[0:len(HEADER_STRING)]
        string = header == HEADER_STRING
        byte = header == HEADER_BYTES
        # if string or byte, strip header and decrypt.
        # if no header is given, return file content
        if string or byte:
            # strip header
            content = content[len(header):]
            # plain text
            content = utila.secret.decrypt(content, string=string)
        elif not self.binary:
            content: str = bytes.decode(content, 'utf8')
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
