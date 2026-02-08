#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import re
import subprocess

import setuptools

ROOT = os.path.dirname(__file__)

with open(os.path.join(ROOT, 'README'), encoding='utf8') as fp:
    README = fp.read()

with open(os.path.join(ROOT, 'utilo/__init__.py'), encoding='utf8') as fp:
    VERSION = re.search(r'__version__ = \'(.*?)\'', fp.read()).group(1)


def version() -> str:
    completed = subprocess.run(
        'git describe'.split(),
        capture_output=True,
    )
    value: str = completed.stdout.strip().decode('utf8')
    if value == VERSION:
        return VERSION
    # transform v2.40.1-5-gc1b4bee to
    # utila-2.93.0.post6+g3b6726a
    value = value[1:]
    value = value.replace('-', '.post', 1)
    value = value.replace('-g', '+g')
    return value


if __name__ == "__main__":
    setuptools.setup(
        author='Helmut Konrad Schewe',
        author_email='info@checkitweg.de',
        description='write it once',
        include_package_data=True,
        long_description=README,
        name='utilo',
        platforms='any',
        url='http://dev.package.checkitweg.de/utilo',
        version=version(),
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.8',
        ],
        packages=[
            'utilo',
            'utilo.classifier',
            'utilo.cli',
            'utilo.feature',
            'utilo.file',
            'utilo.math',
            'utilo.string',
            'utilo.xyz',
        ],
        entry_points={
            'console_scripts': [
                'utilo_lock = utilo.xyz.lock:main',
                'utilo_unlock = utilo.xyz.lock:unlock',
                'utilo_table = utilo.xyz.table:main',
                'utilo_tidy = utilo.xyz.tidy:main',
            ],
        },
    )
