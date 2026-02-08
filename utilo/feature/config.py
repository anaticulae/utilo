# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os

import utilo


def read(config: str) -> dict:
    r"""Read configuration file.

    >>> read("# comment\nconfig = 1.0\none = 1\nstring = helmut hier")
    {'config': 1.0, 'one': 1, 'string': 'helmut hier'}
    """
    result = {}
    for item in config.splitlines():
        item = item.strip()
        if not item:
            continue
        if '#' in item:
            continue
        try:
            name, value = item.split('=', maxsplit=1)
            name = name.strip()
            value = value.strip()
        except ValueError:
            utilo.error(f'could not parse {item}')
            continue
        if value.lower() in {'true', 'false'}:
            result[name] = utilo.str2bool(value)
            continue
        with contextlib.suppress(ValueError):
            value = int(value)
            result[name] = value
            continue
        with contextlib.suppress(ValueError):
            value = float(value)  # pylint:disable=R0204
            result[name] = value
            continue
        result[name] = value
    return result


def overwrite(args):
    """Override command line arguments with arguments passed in a
    configuration file."""
    try:
        configpath = args['config']
    except KeyError:
        return
    if not configpath:
        return
    if not os.path.exists(configpath):
        utilo.exitx(msg=f'config does not exists: {configpath}')
    loaded = utilo.feature.config.read(utilo.file_read(configpath))
    for key, value in loaded.items():
        try:
            utilo.info(f'update {key}:{value}')
            args[key] = value
        except KeyError:
            utilo.error(f'could not update {key}:{value}')
