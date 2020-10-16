# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses
import importlib
import os
import typing

import utila


@dataclasses.dataclass
class FeatureInterface:
    name: str = None
    message: str = None
    command: utila.Command = None
    action: callable = None


FeatureInterfaces = typing.List[FeatureInterface]


def find_features(root: str, featurepackage: str) -> FeatureInterfaces:
    """Locate all feautures in given path

    Ensure that feature methods are defined. If some feature interface
    is not implemented properly, the execution ends with FAILURE."""
    assert os.path.exists(root), root
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
    if not os.path.exists(featurepath):
        utila.error('wrong featurepack configuration, '
                    'check `featurepackage` path')
        utila.error(f'featurepath {featurepath} does not exists')
        exit(utila.FAILURE)
    collected = [
        item.replace('.py', '')
        for item in os.listdir(featurepath)
        if not '__init__' in item and item.endswith('.py')
    ]
    result = []
    ret = 0
    for item in collected:
        current = importlib.import_module(
            featurepackage + '.' + item,
            featurepackage,
        )
        try:
            connected = connect_feature_interface(current, item)
            result.append(connected)
        except AttributeError as exception:
            utila.error(f'SKIP LOADING: {item}')
            utila.error(exception)
            ret += 1
    if ret:
        exit(utila.FAILURE)
    return result


def connect_feature_interface(current, item) -> FeatureInterface:
    """Ensure that feature supports `name`, `commandline` and
    `work`-method."""
    curname = current.name() if hasattr(current, 'name') else item
    message = current.HELP if hasattr(current, 'HELP') else None

    # no commandline information is defined
    def curcommandline():
        return utila.Flag(longcut=curname, message=f'export {curname}')

    if hasattr(current, 'commandline'):
        curcommandline = current.commandline

    return FeatureInterface(
        name=curname,
        message=message,
        command=curcommandline,
        action=current.work,
    )


def prepare_hooks(items: FeatureInterfaces):
    result = {}
    for item in items:
        result[item.name] = item.action
    return result
