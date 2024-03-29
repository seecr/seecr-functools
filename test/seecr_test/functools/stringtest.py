## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2018, 2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

from unittest import TestCase

from seecr.functools.core import reduce, reduced, completing, transduce, is_reduced, unreduced
from seecr.functools.string import strip, rstrip, split


class StringTest(TestCase):
    def test_strip(self):
        # On a string
        self.assertEqual('', strip('', None))
        self.assertEqual('', strip(' \t\r\n \t\r\n '))
        self.assertEqual('AA', strip(' \t\r\n AA \t\r\n '))
        self.assertEqual('', strip(' \t\r\n \t\r\n ', None))
        self.assertEqual('\t\r\n ', strip('\t\r\n x', 'x'))
        self.assertEqual(' \t\r\n ', strip('x \t\r\n x', 'x'))

    def test_rstrip(self):
        # On a string
        self.assertEqual('', rstrip('', None))
        self.assertEqual('', rstrip(' \t\r\n \t\r\n '))
        self.assertEqual(' \t\r\n AA', rstrip(' \t\r\n AA \t\r\n '))
        self.assertEqual('', rstrip(' \t\r\n \t\r\n ', None))
        self.assertEqual('\t\r\n ', rstrip('\t\r\n x', 'x'))
        self.assertEqual('x \t\r\n ', rstrip('x \t\r\n x', 'x'))

    def test_split(self):
        # Bad args
        self.assertRaises(TypeError, lambda: split('str'))
        self.assertRaises(ValueError, lambda: split('str', None))

        # On a string
        self.assertEqual([''], split('', ' '))
        self.assertEqual(['', 'x', '', ''], split(' x  ', ' '))
        self.assertEqual(['x', 'x|x'], split('x|x|x', '|', 1))
        self.assertEqual(['x|x', 'x'], split('x|x||x', '||', 1))
        self.assertEqual(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=2))
        self.assertEqual(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=99))
        self.assertEqual(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=-1))
