#!/usr/bin/env python
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import dirname
from os.path import join
from re import search

from setuptools import setup

ROOT = dirname(__file__)
with open(join(ROOT, 'README.md'), 'rt', encoding='utf8') as fp:
    README = fp.read()

with open(join(ROOT, 'utila/__init__.py'), 'rt', encoding='utf8') as fp:
    VERSION = search(r'__version__ = \'(.*?)\'', fp.read()).group(1)

if __name__ == "__main__":
    setup(
        author='Helmut Konrad Fahrendholz',
        author_email='info@checkitweg.de',
        description='write it once',
        include_package_data=True,
        long_description=README,
        name='utila',
        platforms='any',
        url='http://dev.package.checkitweg.de/utila',
        version=VERSION,
        zip_safe=False,  # create 'zip'-file if True. Don't do it!
        classifiers=[
            'Programming Language :: Python :: 3.8',
        ],
        packages=[
            'utila',
            'utila.classifier',
            'utila.feature',
            'utila.file',
            'utila.math',
            'utila.string',
        ],
    )
