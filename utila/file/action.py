# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import glob
import os
import re
import shutil

import utila


def file_read_lines(path: str, start: int = None, end: int = None) -> str:
    """\
    >>> len(file_read_lines(__file__).splitlines()) > 20
    True
    >>> len(file_read_lines(__file__, 5, 6).splitlines())
    1
    """
    data = utila.file_read(path)
    splitted = data.splitlines(keepends=True)
    start = start or 0
    end = end or len(splitted)
    result = ''.join(splitted[start:end])
    return result


def copy_content(  # pylint:disable=R1260,too-many-branches
        source: str,
        destination: str,
        pattern: str = None,
        ignore: callable = None,
        *,
        recursive: bool = False,
        update: bool = False,
        skip_equal: bool = False,
        verbose: bool = False,
):
    """Copy the content from `source` to `destination` folder. If
    `destination` folder does not exists, it will be created.

    Args:
        source(str): file or directory to copy
        destination(str): directory to copy source item(s)
        pattern(str): accept files which matches this pattern, if None
                      all files matches.
        ignore(callable): option to skip files by path or filename
        recursive(bool): if True, copy child folder
        update(bool): move only when the source file is newer than the
                      destination file or when the destination file is
                      missing.
        skip_equal(bool): if True, do not raise Error if source and
                          destination is equal.
        verbose(bool): explain what is being done

    Pattern-Syntax:
        In the current implementation only one multiple field is
        possible. The multiple pattern group is inside brackets and is
        separated by |. For example: (rawmaker|groupme)__*.yaml, copies
        rawmaker and groupme yaml files.

    Hint:
        Why not using shutil.copytree?: Copy tree expect that
        destination does not exists, but we need this.
    """
    assert source, str(source)
    assert destination, str(destination)
    if os.path.isfile(source):
        _copy_file(source, destination, ignore, update, skip_equal, verbose)
        return
    if pattern is None:
        pattern = '*'

    multiple = split_multipattern(pattern)
    if multiple:
        _copy_multiple(source, destination, pattern, ignore, recursive, update,
                       skip_equal, verbose)
        return

    _copy_folder(source, destination, pattern, recursive, ignore, update,
                 skip_equal, verbose)


def _copy_file(
        source,
        destination,
        ignore,
        update,
        skip_equal,
        verbose,
):
    if ignore and ignore(source):
        utila.debug(f'skip: {source}')
        return
    if not utila.isfilepath(destination):
        destination = os.path.join(destination, os.path.basename(source))
    if verbose:
        utila.log(f'cp: {source} -> {destination}')
    suppress = contextlib.suppress if skip_equal else utila.nothing
    with suppress(shutil.SameFileError):
        utila.file_copy(
            source,
            destination,
            update=update,
            exception=skip_equal,
        )


def _copy_folder(
        source,
        destination,
        pattern,
        recursive,
        ignore,
        update,
        skip_equal,
        verbose,
):
    pattern = f'**/{pattern}' if recursive else pattern

    with utila.chdir(source):
        selected = list(glob.glob(pattern, recursive=recursive))

    suppress = contextlib.suppress if skip_equal else utila.nothing
    for item in selected:
        inpath = os.path.join(source, item)
        if ignore and ignore(inpath):
            utila.debug(f'skip: {inpath}')
            continue
        outpath = os.path.join(destination, item)
        if os.path.isfile(inpath):
            if verbose:
                utila.log(f'cp: {inpath} -> {outpath}')
            with suppress(shutil.SameFileError):
                utila.file_copy(
                    inpath,
                    outpath,
                    update=update,
                    exception=skip_equal,
                )
        else:
            if verbose:
                utila.log(f'mkdir: {outpath}')
            os.makedirs(outpath, exist_ok=True)


def _copy_multiple(
        source,
        destination,
        pattern,
        ignore,
        recursive,
        update,
        skip_equal,
        verbose,
):
    multiple = split_multipattern(pattern)
    if verbose:
        utila.log(f'split pattern: {pattern} -> {multiple}')
    suppress = contextlib.suppress if skip_equal else utila.nothing
    for converted_pattern in multiple:
        # run multiple operation
        with suppress(shutil.SameFileError):
            copy_content(
                source,
                destination,
                ignore=ignore,
                pattern=converted_pattern,
                recursive=recursive,
                skip_equal=skip_equal,
                update=update,
                verbose=verbose,
            )


def split_multipattern(multipattern):
    """Split multiple pattern into several single pattern.

    >>> split_multipattern('(rawmaker|groupme)__*.yaml')
    ['rawmaker__*.yaml', 'groupme__*.yaml']
    """
    # TODO: SUPPORT MULTIPLE GROUPS
    pattern = r'\([\w|\|\_\-]+\)'
    matched = re.match(pattern, multipattern)
    if not matched:
        return None
    match = utila.extract_match(matched)
    result = []
    without_brackets = match[1:-1]
    for item in without_brackets.split('|'):
        result.append(multipattern.replace(match, item))
    return result
