from unittest import TestCase

from seecr.functools.core import reduce, reduced, completing, transduce, is_reduced, unreduced
from seecr.functools.string import strip, split


class StringTest(TestCase):
    def test_strip(self):
        # On a string
        self.assertEquals('', strip('', None))
        self.assertEquals('', strip(' \t\r\n \t\r\n '))
        self.assertEquals('', strip(' \t\r\n \t\r\n ', None))
        self.assertEquals('\t\r\n ', strip('\t\r\n x', 'x'))

    def test_split(self):
        # Bad args
        self.assertRaises(TypeError, lambda: split('str'))
        self.assertRaises(ValueError, lambda: split('str', None))

        # On a string
        self.assertEquals([''], split('', ' '))
        self.assertEquals(['', 'x', '', ''], split(' x  ', ' '))
        self.assertEquals(['x', 'x|x'], split('x|x|x', '|', 1))
        self.assertEquals(['x|x', 'x'], split('x|x||x', '||', 1))
        self.assertEquals(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=2))
        self.assertEquals(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=99))
        self.assertEquals(['x', 'x', 'x'], split('x|x|x', sep='|', maxsplit=-1))
