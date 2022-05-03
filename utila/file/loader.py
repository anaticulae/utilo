# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def from_raw_or_path(
    content: str,
    ftype: str = 'yaml',
    fname: str = None,
) -> str:
    """Provide raw content from file or pass content

    This method enables the interface to get content from filepath,
    directory or use direct raw content.

    Args:
        content(str): filepath or raw content
        ftype(str): file type which is checked
        fname(str): if `content` is directory, and ``directory/fname.ftype``
                    exists, load ``directory/fname.ftype``
    Returns:
        loaded content or raw passed content
    Raises:
        FileNotFoundError: if `content` path not exists
    """
    content = str(content)  # convert `LocalPath` to str
    if content.endswith(f'.{ftype}') and not os.path.exists(content):
        raise FileNotFoundError(f'file not exists: {content}')
    try:
        isdir = utila.NEWLINE not in content and os.path.isdir(content)
    except ValueError:
        # File name is too long, cause testing yaml content as file content.
        isdir = False
    if fname and isdir:
        # use default file path if exists
        if newpath := file_find(content, fnames=fname, ftype=ftype):
            content = newpath
        else:
            raise FileNotFoundError('directory not found:'
                                    f'{content} {fname} {ftype}')
    # filepath must not have any line breaks
    if len(content.splitlines()) == 1 and os.path.isfile(content):
        content = utila.file_read(content)
    return content


def yaml_load(
    content: str,
    fname: str = None,
    ftype: str = 'yaml',
    verify: callable = None,
    safe: bool = True,
):
    loaded = from_raw_or_path(content, ftype=ftype, fname=fname)
    try:
        import yaml  # pylint:disable=import-outside-toplevel
        import yaml.scanner  # pylint:disable=import-outside-toplevel
    except ImportError:  # pragma: no cover
        utila.error('add `yaml` package to requirements, eg. `PyYAML>=5.1`')
        return None
    try:
        if safe:
            result = yaml.safe_load(loaded)
        else:
            result = yaml.load(loaded, Loader=yaml.FullLoader)  #nosec
    except yaml.scanner.ScannerError as error:
        raise ValueError(f'no valid yaml input: {loaded}') from error
    if verify:
        verify(result)
    return result


def yaml_dump(
    content: object,
    safe: bool = True,
):
    r"""\
    >>> yaml_dump(dict(user='Helmut', age=34), safe=False)
    'age: 34\nuser: Helmut\n'
    """
    try:
        import yaml  # pylint:disable=import-outside-toplevel
    except ImportError:  # pragma: no cover
        utila.error('add `yaml` package to requirements, eg. `PyYAML>=5.1`')
        return None
    if safe:
        result = yaml.safe_dump(content)
    else:
        result = yaml.dump(content, Dumper=yaml.Dumper)  #nosec
    return result


def file_find(path, fnames, ftype):
    """Allow multiple file names, select the first one."""
    if isinstance(fnames, str):
        fnames = [fnames]
    for fname in fnames:
        newpath = utila.join(path, f'{fname}.{ftype}')
        if not utila.exists(newpath):
            continue
        return newpath
    return None


class LazyFile:
    """\
    >>> me = LazyFile(__file__)
    >>> assert len(me) > 3000
    >>> assert me == me
    """

    def __init__(self, path):
        self.path = path
        self.content = None

    def lazy(self):
        if self.content is not None:
            return self.content
        self.content = utila.file_read(self.path).strip()
        return self.content

    def __eq__(self, value):
        return str(self) == value

    def __str__(self):
        return self.lazy()

    def __len__(self):
        return len(str(self))


if os.getenv('YAMLFAST', None):
    import pickle  # nosec

    def yaml_dump(content: object, safe: bool = True):  # pylint:disable=W0613,E0102
        dumped = pickle.dumps(content, pickle.HIGHEST_PROTOCOL)
        result = dumped.decode('latin1')
        return result

    def yaml_load(
        content: str,
        fname: str = None,
        ftype: str = 'yaml',
        verify: callable = None,
        safe: bool = True,
    ):  # pylint:disable=W0613,E0102
        raw = from_raw_or_path(
            content,
            ftype=ftype,
            fname=fname,
            # reader=utila.file_read_binary,
        )
        raw: bytes = raw.encode('latin1')
        try:
            result = pickle.loads(raw)  # nosec
        except pickle.UnpicklingError as error:
            raise ValueError('no valid yaml input') from error
        return result
