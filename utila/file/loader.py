# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila.file


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
        newpath = os.path.join(content, f'{fname}.{ftype}')
        if os.path.exists(newpath):
            content = newpath
        else:
            raise FileNotFoundError(f'directory not found: {newpath}')
    # filepath must not have any linebreaks
    if len(content.splitlines()) == 1 and os.path.isfile(content):
        content = utila.file.file_read(content)
    return content


def yaml_from_raw_or_path(
        content: str,
        fname: str = None,
        verify: callable = None,
        safe: bool = True,
):
    loaded = from_raw_or_path(content, ftype='yaml', fname=fname)
    try:
        import yaml
    except ImportError:
        utila.error('add `yaml` package to requirements, eg. `PyYAML>=5.1`')
        return None
    if safe:
        result = yaml.safe_load(loaded)
    else:
        result = yaml.load(loaded, Loader=yaml.FullLoader)  #nosec
    if verify:
        verify(result)
    return result
