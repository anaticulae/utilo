# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import configparser

import utila


def dump_config(config: dict) -> str:
    r"""Dump config to `ini` format.
    >>> dump_config({'header' : {'first': 10, 'second' : 20}})
    '[HEADER]\nfirst = 10\nsecond = 20\n'
    """
    if not config:
        return None

    isflat = isinstance(list(config.values())[0], dict) is False
    result = []
    if isflat:
        for key, value in config.items():
            result.append(f'{key} = {value}'.strip())
    else:
        for header, values in config.items():
            header = header.upper()
            result.append(f'[{header}]')
            for key, value in values.items():
                result.append(f'{key} = {value}'.strip())
    # add final newline
    result.append('')
    return utila.NEWLINE.join(result)


def load_config(raw: str, flat: bool = False) -> dict:
    r"""Load configuration from string.

    >>> load_config('[rawmaker]\nchar_margin = 10\nline_margin = 10.0')
    {'rawmaker': {'char_margin': '10', 'line_margin': '10.0'}}
    >>> load_config('first = 1\nsecond=2', flat=True)
    {'first': '1', 'second': '2'}
    """
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        config.read_string(raw)
    except configparser.MissingSectionHeaderError:
        # support formats without any section
        raw = f'[DEFAULT]\n{raw}'
        config.read_string(raw)
    result = {}
    for section, keys in config.items():
        level = {}
        for key in keys:
            level[key] = config[section][key]
        result[section] = level

    if flat:
        return result['DEFAULT']
    del result['DEFAULT']
    return result
