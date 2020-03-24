# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import importlib
import os
import typing

import utila

FeatureInterface = typing.Tuple[str, utila.Command, callable]
FeatureInterfaces = typing.List[FeatureInterface]


def find_features(root: str, featurepackage: str) -> FeatureInterfaces:
    """Locate all feautures in given path

    Ensure that feature methods are defined. If some feature interface is not
    implemented properly, the exection ends with FAILURE.
    """
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
    assert os.path.exists(root), root
    if not os.path.exists(featurepath):
        utila.error(
            'wrong featurepack configuration, check `featurepackage` path')
        utila.error('featurepath %s does not exists' % featurepath)
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
            result.append(connect_feature_interface(current, item))
        except AttributeError as exception:
            utila.error('SKIP LOADING %s' % item)
            utila.error(exception)
            ret += 1
    if ret:
        exit(utila.FAILURE)
    return result


def connect_feature_interface(current, item) -> FeatureInterface:
    """Ensure that feature supports `name`, `commandline` and `work`-method"""
    curname = current.name() if hasattr(current, 'name') else item

    # no commandline information is defined
    def curcommandline():
        return utila.Flag(longcut=curname, message='export %s' % curname)

    if hasattr(current, 'commandline'):
        curcommandline = current.commandline

    return (curname, curcommandline, current.work)


def prepare_hooks(items: FeatureInterfaces):
    result = {}
    for item in items:
        name, _, caller = item
        result[name] = caller
    return result
