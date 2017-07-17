from unittest import TestCase

# from seecr.functools.core import first, second, identity, some_thread, fpartial, comp, reduce, is_reduced, ensure_reduced, unreduced, reduced, completing, transduce, take
from seecr.functools.string import strip, split


class StringTest(TestCase):
    def test_strip(self):
        # Bad nr-of-args
        self.assertRaises(TypeError, lambda: strip())
        self.assertRaises(TypeError, lambda: strip(None, None, None))

        # On a string
        self.assertEquals('', strip(None, ''))
        self.assertEquals('', strip(None, ' \t\r\n \t\r\n '))
        self.assertEquals('\t\r\n ', strip('x', '\t\r\n x'))
        self.assertEquals('|', strip('xyz', 'zz|xyzyx'))
        self.assertEquals('Hello yz there', strip('yz', 'Hello yz therezy'))

        # As a transducer
        # TODO: !

    def test_split(self):
        # Bad args
        self.assertRaises(TypeError, lambda: split())
        self.assertRaises(TypeError, lambda: split(None, None, None))
        self.assertRaises(TypeError, lambda: split(None, '')) # opts must be a dict with 'sep'
        self.assertRaises(KeyError, lambda: split({}, ''))

        # On a string
        self.assertEquals([''], split({'sep': ' '}, ''))
        self.assertEquals([''], split({'sep': 'x'}, ''))
        self.assertEquals(['', 'x', '', 'y\n\r\tz'], split({'sep': ' '}, ' x  y\n\r\tz'))
        self.assertEquals(['', '', '', ''], split({'sep': ' '}, '   ')) # 3-spaces-string
        self.assertEquals(['', 'x'], split({'sep': 'xx'}, 'xxx'))
        self.assertEquals(['', '', 'x'], split({'sep': 'xx'}, 'xxxxx'))
        self.assertEquals(['aap', 'noot', 'mies'], split({'sep': ','}, 'aap,noot,mies'))
        self.assertEquals(['a,nt,ms'], split({'sep': ',', 'maxsplit': 0}, 'a,nt,ms'))
        self.assertEquals(['a', 'nt,ms'], split({'sep': ',', 'maxsplit': 1}, 'a,nt,ms'))
        self.assertEquals(['a', 'nt', 'ms'], split({'sep': ',', 'maxsplit': 2}, 'a,nt,ms'))
        self.assertEquals(['a', 'nt', 'ms'], split({'sep': ',', 'maxsplit': 99}, 'a,nt,ms'))
        self.assertEquals(['a', 'nt', 'ms'], split({'sep': ',', 'maxsplit': -1}, 'a,nt,ms'))

        # As a transducer
        # TODO: !
