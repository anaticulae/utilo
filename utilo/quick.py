# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import importlib.metadata
import re

import setuptools

import utilo

AUTHOR = 'Helmut Konrad Schewe'
AUTHOR_EMAIL = 'helmutus@outlook.com'

CLASSIFIERS = [
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
]

URL = 'https://github.com/anaticulae/'


def install(
    root: str,
    include_package_data: bool = True,
):
    root = utilo.make_absolute(str(root))
    utilo.log(f'install: {root}')
    module = utilo.load_module(root)
    xpackages = packages(module)
    xentry = entry_points(module)
    root = utilo.baw_root(root)
    short = utilo.baw_name(root)
    xreadme = readme(root)
    xrequires = requires(root)
    xpackage_data = package_data(module)
    description = utilo.baw_desc(root)
    setuptools.setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=description,
        classifiers=CLASSIFIERS,
        entry_points=xentry,
        include_package_data=include_package_data,
        install_requires=xrequires,
        long_description=xreadme,
        name=short,
        package_data=xpackage_data,
        packages=xpackages,
        platforms='any',
        url=f'{URL}{short}',
        version=current(root),
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
    )


def packages(module):
    """\
    >>> import collections; Module=collections.namedtuple('Module', 'PACKAGES')
    >>> packages(Module('first second third'.split()))
    ['first', 'second', 'third']
    >>> PACKAGES=['first', 'second', 'third'],
    >>> packages(Module(PACKAGES))
    Traceback (most recent call last):
      ...
    ValueError: require list or single tuple: (['first', 'second', 'third'],)
    """
    result = module.PACKAGES
    if not all(isinstance(item, str) for item in result):
        # PACKAGES = [
        # 'lists',
        # 'lists.features',
        # 'lists.strategies',
        # ], <-ATTENTION COMMA!
        raise ValueError(f'require list or single tuple: {result}')
    return result


def entry_points(module):
    """\
    >>> import collections; Module=collections.namedtuple('Module', 'entry_points')
    >>> entry_points(Module(dict()))
    Traceback (most recent call last):
    ...
    ValueError: require upper-case: entry_points:...
    """
    if hasattr(module, 'entry_points'):
        raise ValueError(f'require upper-case: entry_points: {dir(module)}')
    try:
        entry = module.ENTRY_POINTS
    except AttributeError:
        entry = None
    return entry


def package_data(module):
    try:
        return module.PACKAGE_DATA
    except AttributeError:
        return {}


def version(package):
    """Determine precise package version/githash.

    >>> import utilo; version(utilo)
    '...'
    >>> import re; version(re)
    Traceback (most recent call last):
        ...
    ValueError: re not installed/no metadata
    """
    assert not isinstance(package, str), f'require module: {package}'
    name = package.__name__
    try:
        live = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError as notfound:
        raise ValueError(f'{name} not installed/no metadata') from notfound
    return live


def requires(root) -> list:
    """\
    >>> requires(__file__)
    []
    """
    root = utilo.baw_root(root)
    path = utilo.join(root, 'requirements.txt')
    if not utilo.exists(path):
        return []
    content = utilo.file_read(path)
    result = [line for line in content.splitlines() if line and '#' not in line]
    return result


def readme(root):
    for name in 'README README.md README.rst'.split():
        path = utilo.join(root, name)
        if utilo.exists(path):
            return utilo.file_read(path)
    raise ValueError(f'could not locate any README: {root}')


def current(root, backup: bool = False):
    """\
    >>> current(__file__, backup=True) == utilo.__version__
    True
    """
    root = utilo.baw_root(root)
    backup |= not utilo.hasprog('git')
    # git is installed, but no git repository is available
    backup |= not utilo.exists(utilo.join(root, '.git'))
    if backup:
        package = utilo.baw_name(root)
        content = utilo.file_read(utilo.join(root, package, '__init__.py'))
        result = re.search(
            r'__version__ = \'(.*?)\'',
            content,
        ).group(1)
        return result
    return git_hash(root)


def git_hash(root) -> str:
    """\
    >>> git_hash('.')
    '...'
    """
    if not utilo.hasprog('git'):
        utilo.exitx('install git, please')
    completed = utilo.run(
        'git describe',
        cwd=root,
        expect=None,
    )
    value = completed.stdout.strip()
    if value == 'empty!':
        # no git repository available
        return static(root)
    if value == static(root):
        return value
    # transform v2.40.1-5-gc1b4bee to
    # utilo-2.93.0.post6+g3b6726a
    value = value[1:]
    value = value.replace('-', '.post', 1)
    value = value.replace('-g', '+g')
    return value


def static(root):
    short = utilo.baw_name(root)
    if not short:
        utilo.exitx(msg=f'missing short `{short}` def in .baw: {root}')
    path = utilo.join(root, short, '__init__.py', exist=True)
    content = utilo.file_read(path)
    result = re.search(r'__version__ = \'(.*?)\'', content).group(1)
    return result
