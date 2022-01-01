# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import re

import utila.feature


def prepare_outputpath(outputstep, result, rename: callable = None):
    outputstep, result = replace_filepaths(outputstep, result)
    outputstep, result = replace_datatype_pattern(outputstep, result)
    outputstep = replace_star_pattern(outputstep, result, rename=rename)
    outputstep = replace_filehash_pattern(outputstep, result)
    return outputstep, result


def replace_filepaths(outputstep, result):
    """Define path to write by list of (path, content) and write to
    absoult path.

    {FILEPATHS}

    This feature is used to modify existing resources.
    """
    if not any(isfilepath(item) for item in outputstep):
        return outputstep, result
    # TODO: HACKY
    # path to write
    outputstep = [item[0] for item in result]
    # content to write
    result = [item[1] for item in result]
    return outputstep, result


def replace_datatype_pattern(outputstep, result):  # pylint:disable=R1260
    # TODO: DIRTY
    datatype = variable_datatype(outputstep)
    parameter = variable_parameter(outputstep)
    if datatype and not parameter:
        if len(outputstep) == 1:
            if isinstance(result, tuple):
                result, ext = result
                outputstep = [replace_ext(outputstep[0], ext)]
                result = (result,)
        else:
            assert 0, 'not handled'
    elif datatype == 1 and parameter == 1:
        out, res = [], []
        if len(outputstep) == 1:
            for index, item in enumerate(result):
                content, ext = item
                path = outputstep[0].replace('*', f'{index}')
                path = replace_ext(path, ext)
                out.append(path)
                res.append(content)
            outputstep, result = out, res
        else:
            assert 0, 'not handled'
    elif datatype and parameter:
        out, res = [], []
        for index, item in enumerate(result):
            path_line, res_line = [], []
            for step, content in zip(outputstep, item):
                path = step.replace('*', f'{index}')
                if not isinstance(content, (str, bytes)):
                    content, ext = content
                    path = replace_ext(path, ext)
                path_line.append(path)
                res_line.append(content)
            out.append(path_line)
            res.append(res_line)
        outputstep, result = out, res
    return outputstep, result


def replace_star_pattern(outputstep, result, rename: callable = None):
    variable_returnvalues = variable_parameter(outputstep)
    if not variable_returnvalues:
        return outputstep
    starpattern = [
        item for item in outputstep if '*' in item or '{FILEHASHS}' in item
    ]  # HACK
    if not starpattern:
        # TODO: REMOVE THIS HACK, CHANGE CHECK IN VARIABLE PARAMETER
        # THIS HACK IS REQUIRED CAUSE START PATTEN RESOLVER HANDLES STEPS
        # WITH VARIABLE EXTENTION NOT CORRECTLY
        return outputstep
    # Create parent folder if required:
    # cli_example__multistep_pages/view_*.html
    # adding list of files in parent folder is possible.
    parent = utila.path_parent(outputstep[0])
    if result:
        if rename:
            parent = rename(parent)
        # only create output folder if some content is to write
        os.makedirs(parent, exist_ok=True)
    # replace star-pattern to archive indexed output paths
    if variable_returnvalues == 1:
        outputstep = outputstep[0]
        outputstep = [
            outputstep.replace('*', f'{index}')
            for index, _ in enumerate(result)
        ]
        return outputstep
    multiple_start = []
    for index in range(len(result)):
        line = []
        for item in outputstep:
            if isinstance(item, str):
                line.append(item.replace('*', f'{index}'))
            else:
                line.append(tuple(it.replace('*', f'{index}') for it in item))
        multiple_start.append(tuple(line))
    return multiple_start


def replace_filehash_pattern(outputstep, resultcontent):
    result = []
    for path, content in zip(outputstep, resultcontent):
        if isinstance(path, str):
            path = replace_filehash(0, path, [content])
        else:
            path = [
                replace_filehash(index, item, content)
                for index, item in enumerate(path)
            ]
        result.append(path)
    return result


def replace_filehash(index: int, path: str, content):
    # support multiple file HASHS pattern
    path = path.replace('{FILEHASHS}', '{FILEHASH}')
    if '{FILEHASH}' in path:
        replacement = utila.freehash(content[index])
        path = path.replace('{FILEHASH}', replacement)
        return path

    number = filenumber(path)
    if number is None:
        return path

    replacement = utila.freehash(content[number])
    pattern = '{FILEHASH_' + str(number) + '}'
    path = path.replace(pattern, replacement)
    return path


def replace_ext(path, ext):
    if '???' not in path:
        return path
    # TODO: THIS IS JUST A HACK, WHICH PREVENT PROBLEMS IN PATTERN
    # REPLACER
    path = path.replace('{FILEHASHS}', '{FILEHASH}')
    result = path.replace('???', ext)
    return result


def filenumber(item: str) -> int:
    """\
    >>> filenumber('{FILEHASH_4}')
    4
    """
    pattern = r'\{FILEHASH\_(?P<number>\d{1,2})\}'
    matched = re.search(pattern, item)
    if not matched:
        return None
    result = int(matched['number'])
    return result


def variable_parameter(items: list) -> int:
    """Count number of path contains */{FILEHASH}-pattern to replace."""
    result = [
        item for item in items
        if '*' in item or isfilehash(item) or isfilepath(item)
    ]
    result = len(result)
    return result


def isfilehash(item):
    # {FILEHASH to support {FILEHASH_NUMBER Pattern
    return '{FILEHASH}' in item or '{FILEHASH' in item


def isfilepath(item):
    return '{FILEPATHS}' in item


def variable_datatype(items: list) -> int:
    """Count number of path ends with ???-pattern to replace datatype."""
    result = len([item for item in items if item.endswith('???')])
    return result
