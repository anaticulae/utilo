# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import re
import sys
import zipfile

import utila


def simple_call(call: str) -> str:
    """Extract configuration of called program.

    >>> simple_call('rawmaker -j=auto -i C:/toc.pdf -o C:/master_page_ --char_margin=3.1 --boxes_f')
    'rawmaker --boxes_f --char_margin=3.1'
    >>> simple_call('rawmaker -i privacy_data_protection_whitepaper-de.pdf')
    'rawmaker'
    """
    # remove processor number
    call = re.sub(r'-j(=|\s{1,5})(auto|\d{1,2})', '', call)
    # remove input and output
    call = re.sub(r'-(i|o)(=|\s{1,5})[^ ]+\b', '', call)
    if ' ' in call.strip():
        program, parameter = call.split(maxsplit=1)
        parameter = ' '.join(sorted(parameter.split()))
    else:
        program, parameter = call, ''
    return f'{program} {parameter}'.strip()


def inputs(call: str) -> list:
    """\
    >>> inputs('rawmaker -j=auto -i C:/page_72_noimages_toc.pdf -o C:/noimages_toc -i=/c/input --boxes_f')
    ['C:/page_72_noimages_toc.pdf', '/c/input']
    >>> inputs('rawmaker -i privacy_data_protection_whitepaper-de.pdf --images')
    ['privacy_data_protection_whitepaper-de.pdf']
    """
    result = []
    for item in re.finditer(r'-i(=|\s{1,5})(?P<source>[^ ]+)\b', call):
        result.append(item['source'])
    return result


def output(call: str) -> str:
    """\
    >>> output('rawmaker -j=auto -i C:/page_72_noimages_toc.pdf -o C:/noimages_toc -i=/c/input --boxes_f')
    'C:/noimages_toc'
    """
    matched = re.search(r'-o(=|\s{1,5})(?P<output>[^ ]+)\b', call)
    if not matched:
        return None
    return matched['output']


def datapackage(call: str, version: str) -> str:
    try:
        cached = os.environ['UTILA_CACHE']
    except KeyError:
        return None
    sources = inputs(call)
    hashed = utila.directory_hash(sources, ftype=('yaml', 'png', 'pdf'))
    if hashed is None:
        hashed = utila.freehash([])
    simple = simple_call(call).strip()
    if ' ' in simple:
        program, parameter = simple.split(maxsplit=1)
    else:
        program, parameter = simple, ''
    parameter = utila.freehash(parameter)
    cached = os.path.join(cached, program, version, hashed, parameter)
    return cached


def use_cache(program, version, argv=None) -> int:
    """\
    cache does not exists
    >>> use_cache('rawmaker', '1.3.2', ['-h'])
    False
    """
    argv = argv if argv else []
    call = ' '.join([program] + argv)
    cached = utila.datapackage(call, version=version)
    if not cached:
        # no cache
        if not utila.testing():
            utila.debug('no cache')
        return False
    if not os.path.exists(cached):
        return False
    utila.log('use cache')
    outpath = output(call)
    if not outpath:
        outpath = os.getcwd()
    os.makedirs(outpath, exist_ok=True)
    todo = f'python -m zipfile -e {cached} {outpath}'
    extracted = utila.run(todo)
    return extracted.returncode == utila.SUCCESS


def write_cache(program, version, argv=None) -> bool:
    argv = argv if argv else []
    call = ' '.join([program] + argv)
    cached = utila.datapackage(call, version=version)
    if not cached:
        # no cache
        utila.debug('no cache')
        return False
    if os.path.exists(cached):
        # TODO: ADD OPTION TO UPDATE CACHE
        return True
    outpath = output(call)
    if not outpath:
        outpath = os.getcwd()
    parent_cache = utila.forward_slash(os.path.split(cached)[0])
    os.makedirs(parent_cache, exist_ok=True)
    collected = utila.file_list(
        outpath,
        include=['yaml', 'png'],
    )
    with zipfile.ZipFile(cached, 'w') as archive:
        for item in collected:
            archive.write(item, arcname=item)
    return True


@contextlib.contextmanager
def cacheme(program, version):
    argv = sys.argv[1:]
    if use_cache(program, version=version, argv=argv):
        yield True
    else:
        yield False
    write_cache(program, version, argv=argv)
