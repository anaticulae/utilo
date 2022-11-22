# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re

import setuptools

import utila

AUTHOR = 'Helmut Konrad Fahrendholz'
AUTHOR_EMAIL = 'helmutus@outlook.com'

CLASSIFIERS = [
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
]


def install(root: str):
    module = utila.load_module(root)
    packages = module.PACKAGES
    try:
        entry = module.ENTRY_POINTS
    except AttributeError:
        entry = None
    root = utila.baw_root(root)
    short = utila.baw.baw_name(root)
    xreadme = readme(root)
    description = utila.baw_desc(root)
    setuptools.setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=description,
        include_package_data=True,
        long_description=xreadme,
        name=short,
        platforms='any',
        url=f'https//pip.ostia.la/{short}',
        version=version(root),
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=CLASSIFIERS,
        packages=packages,
        entry_points=entry,
    )


def readme(root):
    for name in 'README README.md README.rst'.split():
        path = utila.join(root, name)
        if utila.exists(path):
            return utila.file_read(path)
    raise ValueError(f'could not locate any README: {root}')


def version(root) -> str:
    if not utila.hasprog('git'):
        utila.exitx('install git, please')
    completed = utila.run(
        'git describe',
        cwd=root,
    )
    value = completed.stdout.strip()
    if value == static(root):
        return value
    # transform v2.40.1-5-gc1b4bee to
    # utila-2.93.0.post6+g3b6726a
    value = value[1:]
    value = value.replace('-', '.post', 1)
    value = value.replace('-g', '+')
    return value


def static(root):
    short = utila.baw.baw_name(root)
    path = utila.join(root, short, '__init__.py', exist=True)
    content = utila.file_read(path)
    result = re.search(r'__version__ = \'(.*?)\'', content).group(1)
    return result
