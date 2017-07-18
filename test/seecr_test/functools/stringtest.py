from unittest import TestCase

from seecr.functools.core import reduce, reduced, completing, transduce, is_reduced, unreduced
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
        self.fail('todo')

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
        _log = []
        def test_f(retval):
            def f(*a):
                _log.append(a)
                return retval
            return f

        def log():
            _l = _log[:]
            del _log[:]
            return _l

        # 0-arity
        f = test_f('')
        self.assertEquals('', split({'sep': ','})(f)())
        self.assertEquals([()], log())
        f = test_f(',,')        # Input == output
        self.assertEquals(',,', split({'sep': ','})(f)())
        self.assertEquals([()], log())

        # 1-arity
        f = test_f('aap2')
        self.assertEquals('aap2', split({'sep': ','})(f)('aap1'))
        self.assertEquals([('aap1',)], log())
        f = test_f(',,')                                           # Done: input == output
        self.assertEquals(',,', split({'sep': ','})(f)('in,put'))  # Done: input == output
        self.assertEquals([('in,put',)], log())

        # 2-arity - basics
        f = test_f('whatever2')
        self.assertEquals('whatever2', split({'sep': ','})(f)('whatever', 'aap,noot,mies'))
        self.assertEquals([
            ('whatever', 'aap'),
            ('whatever2', 'noot'),
            ('whatever2', 'mies'),
        ], log())

        # 2-arity - reduced
        f = test_f(reduced('whatever_stop_now!'))
        r = split({'sep': ','})(f)('whatever', 'aap,noot,mies')
        self.assertTrue(is_reduced(r))
        self.assertEquals('whatever_stop_now!', unreduced(r))
        self.assertEquals([
            ('whatever', 'aap'),
        ], log())

        # real-world via transduce
        def a(acc, e):
            acc.append(e)
            return acc
        self.assertEquals(['str', 'in', 'put', 'h', '', 'ere'], transduce(split({'sep': ';'}), completing(a), [], ['str', 'in;put', 'h;;ere']))
