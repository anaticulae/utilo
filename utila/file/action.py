# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2022 by Helmut Konrad Fahrendholz. All rights reserved.
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


def file_read_lines(
    path: str,
    start: int = None,
    end: int = None,
    private: bool = False,
) -> str:
    """\
    >>> len(file_read_lines(__file__).splitlines()) > 20
    True
    >>> len(file_read_lines(__file__, 5, 6).splitlines())
    1
    """
    data = utila.file_read(path, private=private)
    splitted = data.splitlines(keepends=True)
    start = start or 0
    end = end or len(splitted)
    result = ''.join(splitted[start:end])
    return result


def copy_content(  # pylint:disable=R1260,too-many-branches
    src: str,
    dest: str,
    pattern: str = None,
    ignore: callable = None,
    rename: callable = None,
    *,
    recursive: bool = False,
    update: bool = False,
    skip_equal: bool = False,
    verbose: bool = False,
    private: bool = False,
    unlock: bool = False,
):
    """Copy the content from `src` to `dest` folder. If `dest` folder
    does not exists, it will be created.

    Args:
        src(str): file or directory to copy
        dest(str): directory to copy src item(s)
        pattern(str): accept files which matches this pattern, if None
                      all files matches.
        ignore(callable): option to skip files by path or filename
        rename(callable): rename written files
        recursive(bool): if True, copy child folder
        update(bool): move only when the src file is newer than the
                      dest file or when the dest file is missing.
        skip_equal(bool): if True, do not raise Error if src and
                          dest is equal.
        verbose(bool): explain what is being done
        private(bool): encrypt data
        unlock(bool): if True, remove file lock

    Pattern-Syntax:
        In the current implementation only one multiple field is
        possible. The multiple pattern group is inside brackets and is
        separated by |. For example: (rawmaker|groupme)__*.yaml, copies
        rawmaker and groupme yaml files.

    Hint:
        Why not using shutil.copytree?: Copy tree expect that
        dest does not exists, but we need this.
    """
    assert src, str(src)
    assert dest, str(dest)
    if os.path.isfile(src):
        _copy_file(src, dest, ignore, rename, update, skip_equal, verbose,
                   private, unlock)
        return
    if pattern is None:
        pattern = '*'

    multiple = split_multipattern(pattern)
    if multiple:
        _copy_multiple(src, dest, pattern, ignore, rename, recursive, update,
                       skip_equal, verbose, private, unlock)
        return
    _copy_folder(src, dest, pattern, recursive, ignore, rename, update,
                 skip_equal, verbose, private, unlock)


def _copy_file(
    src,
    dest,
    ignore,
    rename,
    update,
    skip_equal,
    verbose,
    private,
    unlock: bool = False,
):
    if ignore and ignore(src):
        utila.debug(f'skip: {src}')
        return
    if not utila.isfilepath(dest):
        filename = os.path.basename(src)
        dest = os.path.join(dest, filename)
        if rename:
            dest = rename(dest)
    if verbose:
        utila.log(f'cp: {src} -> {dest}')
    suppress = contextlib.suppress if skip_equal else utila.nothing
    with suppress(shutil.SameFileError):
        utila.file_copy(
            src,
            dest,
            update=update,
            exception=skip_equal,
            private=private,
            unlock=unlock,
        )


def _copy_folder(  # pylint:disable=R0913,R0914
    src,
    dest,
    pattern,
    recursive,
    ignore,
    rename,
    update,
    skip_equal,
    verbose,
    private,
    unlock: bool = False,
):
    pattern = f'**/{pattern}' if recursive else pattern
    with utila.chdir(src):
        # TODO: NOT THREAD SAFE!
        selected = list(glob.glob(pattern, recursive=recursive))
    suppress = contextlib.suppress if skip_equal else utila.nothing
    for item in selected:
        inpath = os.path.join(src, item)
        if ignore and ignore(inpath):
            utila.debug(f'skip: {inpath}')
            continue
        outpath = os.path.join(dest, item)
        if rename:
            outpath = rename(outpath)
        if os.path.isfile(inpath):
            if verbose:
                utila.log(f'cp: {inpath} -> {outpath}')
            with suppress(shutil.SameFileError):
                utila.file_copy(
                    inpath,
                    outpath,
                    update=update,
                    exception=skip_equal,
                    private=private,
                    unlock=unlock,
                )
        else:
            if verbose:
                utila.log(f'mkdir: {outpath}')
            os.makedirs(outpath, exist_ok=True)


def _copy_multiple(  # pylint:disable=R0913
    src,
    dest,
    pattern,
    ignore,
    rename,
    recursive,
    update,
    skip_equal,
    verbose,
    private,
    unlock: bool = False,
):
    multiple = split_multipattern(pattern)
    if verbose:
        utila.log(f'split pattern: {pattern} -> {multiple}')
    suppress = contextlib.suppress if skip_equal else utila.nothing
    for converted_pattern in multiple:
        # run multiple operation
        with suppress(shutil.SameFileError):
            copy_content(
                src,
                dest,
                ignore=ignore,
                rename=rename,
                pattern=converted_pattern,
                recursive=recursive,
                skip_equal=skip_equal,
                update=update,
                verbose=verbose,
                private=private,
                unlock=unlock,
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
