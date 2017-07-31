# -*- coding: utf-8 -*-
## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2017 Seecr (Seek You Too B.V.) http://seecr.nl
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

from os import getuid
assert getuid() != 0, "Do not run tests as 'root'"

from os import system                            #DO_NOT_DISTRIBUTE
system('find .. -name "*.pyc" | xargs rm -f')    #DO_NOT_DISTRIBUTE
from seecrdeps import includeParentAndDeps       #DO_NOT_DISTRIBUTE
includeParentAndDeps(__file__, scanForDeps=True) #DO_NOT_DISTRIBUTE

import unittest
from warnings import simplefilter
simplefilter('default')

from seecr_test.functools.coretest import CoreTest
from seecr_test.functools.wrangletest import WrangleTest
from seecr_test.functools.stringtest import StringTest


if __name__ == '__main__':
    unittest.main()
