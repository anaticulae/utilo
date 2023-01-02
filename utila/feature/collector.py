# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses
import importlib
import os

import utila


@dataclasses.dataclass
class FeatureHooks:
    before: callable = None
    work: callable = None
    after: callable = None
    error: callable = None


@dataclasses.dataclass
class FeatureInterface:
    name: str = None
    message: str = None
    command: utila.Command = None
    hooks: FeatureHooks = None


FeatureInterfaces = list[FeatureInterface]


def find_features(root: str, featurepackage: str) -> FeatureInterfaces:
    """Locate all features in given path

    Ensure that feature methods are defined. If some feature interface
    is not implemented properly, the execution ends with FAILURE."""
    utila.exists_assert(root)
    featurepath = os.path.join(root, featurepackage.replace('.', '/'))
    if not os.path.exists(featurepath):
        msg = 'wrong featurepack configuration,\n check `featurepackage` path'
        utila.exitx(f'{msg}\n featurepath {featurepath} does not exists')
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
        utila.exitx()
    return result


def connect_feature_interface(current, item) -> FeatureInterface:
    """Ensure that feature supports `name`, `commandline` and
    `work`-method."""
    curname = current.name() if hasattr(current, 'name') else item
    message = getattr(current, 'HELP', None)

    before = getattr(current, 'before', None)
    after = getattr(current, 'after', None)
    error = getattr(current, 'error', None)

    assert before is None or callable(before), f'require callable, {current}'
    assert after is None or callable(after), f'require callable, {current}'
    assert error is None or callable(error), f'require callable, {current}'

    # no command line information is defined
    def curcommandline():
        return utila.Flag(longcut=curname, message=f'export {curname}')

    if hasattr(current, 'commandline'):
        curcommandline = current.commandline

    hooks = FeatureHooks(
        before=before,
        work=current.work,
        after=after,
        error=error,
    )

    return FeatureInterface(
        name=curname,
        message=message,
        command=curcommandline,
        hooks=hooks,
    )
