#!/usr/bin/env python
## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2011-2014, 2018, 2022 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Functools"
#
# "Seecr Functools" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Functools" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Functools"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here/"README.md").read_text(encoding="utf-8")

version = '$Version: 0$'[9:-1].strip()

packages=find_packages(exclude=('seecr',))
packages=find_packages() #DO_NOT_DISTRIBUTE

setup(
    name='seecr-functools',
    version=version,
    packages=packages,
    url='http://www.seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description='Functional Tools for Seecr',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms=['linux'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3',
    ]
)
