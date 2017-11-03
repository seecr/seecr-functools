#!/usr/bin/env python
## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2011-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from distutils.core import setup

version = '$Version: 1.4.x$'[9:-1].strip()

setup(
    name='seecr-functools',
    packages=[
        "seecr", # DO_NOT_DISTRIBUTE
        "seecr.functools"
    ],
    version=version,
    url='http://www.seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description='Functional Tools for Seecr',
    long_description='Functional Tools to make life easier for Seecr people.',
    platforms=['linux'],
)
