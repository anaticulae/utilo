# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import os
import re

import utila

DESCRIPTION = """\
Parse column file and replace with beautified file.
"""


@utila.saveme
def main():
    paths = sources()
    for path in paths:
        utila.log(path)
        content = utila.file_read(path)
        content = action(content)
        utila.file_replace(path, content)
    utila.exitx(returncode=utila.SUCCESS)


SPACE_MIN = 30

COLUMNS = 2


def action(
    content: str,
    space_min=SPACE_MIN,
    separator=None,
    sortby_column: int = 0,
) -> str:
    r"""\
    >>> action('Hier           spricht\nDer Mut           Helmut\nSchelm', 5)
    'Der Mut     Helmut\nHier        spricht\nSchelm\n'
    >>> action('')
    '\n'
    """
    if separator:
        separator = re.escape(separator)
    content = content.strip()
    collected = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if separator is None:
            # split data by spaces
            collected.append(re.split(r'[ ]{5,}', line, maxsplit=COLUMNS - 1))
        else:
            collected.append(re.split(separator, line))
    if not collected:
        return utila.NEWLINE
    if sortby_column is not None:
        collected.sort(key=lambda x: utila.alphabetically(x[sortby_column]))  # pylint:disable=C3001
    column_wdith = max(len(item[0]) for item in collected) + space_min
    result = []
    for item in collected:
        if len(item) == 1:
            result.append(item[0])
            continue
        # TODO: DIRTY
        line = item[0] + ' ' * (column_wdith - len(item[0])) + item[1]
        result.append(line)
    result: str = utila.NEWLINE.join(result)
    # ensure newline at the end
    result: str = utila.final_newline(result)
    return result


def sources() -> list:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'files',
        type=str,
        nargs='+',
        help='files to process',
    )
    parser.add_argument(
        'seperator',
        type=str,
        default=' ',
        help='split column by separator',
    )
    args = parser.parse_args()
    result = [utila.make_absolute(item) for item in args.files]
    failure = False
    for item in result:
        if os.path.exists(item):
            if os.path.isfile(item):
                continue
            utila.error(f'not a file: {item}')
        else:
            utila.error(f'file does not exists: {item}')
        failure = True
    if failure:
        utila.exitx()
    return result
