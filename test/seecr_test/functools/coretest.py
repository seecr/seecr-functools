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

from __future__ import absolute_import

import __builtin__

from unittest import TestCase

from copy import deepcopy, copy
from types import GeneratorType

from seecr.functools.core import first, second, identity, some_thread, fpartial, comp, reduce, is_reduced, ensure_reduced, unreduced, reduced, completing, transduce, take, cat, map, run, filter, complement, remove, juxt, truthy, append, strng, trampoline, thrush, constantly, before, after, interpose, interleave, assoc_in, update_in, assoc, assoc_in_when, sequence, get_in, assoc_when, update_in_when, iterate, last
from seecr.functools.string import strip, split

builtin_next = __builtin__.next
l = list


class CoreTest(TestCase):
    def testIdentity(self):
        self.assertRaises(TypeError, lambda: identity())
        self.assertRaises(TypeError, lambda: identity(1, 2))
        self.assertEquals(1, identity(1))
        o = object()
        self.assertTrue(o is identity(o))

    def test_truthy(self):
        self.assertEquals(False, truthy(0))
        self.assertEquals(False, truthy(''))
        self.assertEquals(False, truthy([]))
        self.assertEquals(False, truthy({}))
        self.assertEquals(False, truthy(None))
        self.assertEquals(False, truthy(False))

        self.assertEquals(True, truthy(1))
        self.assertEquals(True, truthy(-1))
        self.assertEquals(True, truthy('-'))
        self.assertEquals(True, truthy([0]))
        self.assertEquals(True, truthy({'x': 'y'}))
        self.assertEquals(True, truthy(True))

    def testFirst(self):
        self.assertEquals(None, first(None))
        self.assertEquals(None, first([]))
        g = (x for x in [])
        self.assertEquals(None, first(g))
        self.assertEquals("a", first(["a"]))
        self.assertEquals("a", first(["a", "b"]))
        g = (x for x in [42])
        self.assertEquals(42, first(g))

        self.assertEquals('-', first(None, default='-'))
        self.assertEquals('-', first([], default='-'))
        self.assertEquals('-', first((x for x in []), default='-'))

    def testSecond(self):
        self.assertEquals(None, second(None))
        self.assertEquals(None, second([]))
        self.assertEquals(None, second([1]))
        self.assertEquals(2, second([1, 2]))
        self.assertEquals(2, second([1, 2, 3]))

        self.assertEquals('-', second(None, default='-'))
        self.assertEquals('x', second([], default='x'))
        self.assertEquals('-', second([1], default='-'))
        self.assertEquals(2, second([1, 2], default='-'))
        self.assertEquals(2, second([1, 2, 3], default='-'))

    def testLast(self):
        self.assertEquals(None, last(None))
        self.assertEquals(None, last([]))
        self.assertEquals(1, last([1]))
        self.assertEquals(2, last([1, 2]))
        self.assertEquals(3, last(x for x in [1, 2, 3]))

        self.assertEquals('-', last(None, default='-'))
        self.assertEquals('x', last([], default='x'))
        self.assertEquals(1, last([1], default='-'))
        self.assertEquals(2, last([1, 2], default='-'))
        self.assertEquals(3, last((x for x in [1, 2, 3]), default='-'))

    def testThrush(self):
        self.assertRaises(TypeError, lambda: thrush())

        # Wrong or at least weird, but does not crash with this impl.:
        self.assertEquals('a', thrush('a'))

        self.assertEquals('a>', thrush('a', lambda v: v+'>'))
        f = lambda v: v+'>'
        self.assertEquals('a>>>!', thrush('a', f, f, f, lambda v: v+'!'))

    def testConstantly(self):
        f = constantly('x')
        self.assertEquals('x', f())
        self.assertEquals('x', f('a'))
        self.assertEquals('x', f('a', k='w'))
        self.assertEquals('x', f('a', 'b', k='w', k2='w2'))

        f = constantly([{'zz'}])
        self.assertEquals([{'zz'}], f())

    def testGet_in(self):
        # empty keypath: in->out
        self.assertEquals({}, get_in({}, []))
        self.assertEquals({}, get_in({}, ()))

        # non-existing path
        self.assertEquals(None, get_in({}, ('a')))
        self.assertEquals(None, get_in({}, ['a', 'b', 'c']))
        self.assertEquals(None, get_in({}, ('a', 'b', 'c')))

        # existing path
        self.assertEquals('X', get_in({'a': 'X'}, ['a']))
        self.assertEquals({'b': 'bb'}, get_in({'a': {'b': 'bb'}}, ['a']))
        self.assertEquals('bb', get_in({'a': {'b': 'bb'}}, ['a', 'b']))
        self.assertEquals('bb', get_in({'a': {'b': 'bb'}}, ('a', 'b'))) # tuple

        # tail does not exist
        self.assertEquals(None, get_in({'a': {'b': 'X'}}, ['a', 'y']))
        self.assertEquals(None, get_in({'a': {'b': 'X'}}, ('a', 'y')))
        self.assertEquals(None, get_in({'a': {'b': {'c': 'X'}}}, ['a', 'b', 'y', 'z']))

        # other default
        self.assertEquals('not-found', get_in({}, ['a', 'b', 'y', 'z'], 'not-found'))

        # errors
        try:
            get_in({'a': 'X'}, ['a', 'b'])
        except TypeError, e:
            self.assertEquals("string indices must be integers, not str (on accessing ['a', 'b'] in {'a': 'X'})", str(e))
        else: self.fail()

        try:
            get_in({'a': {'b': {'c': 'X'}}}, ['a', 'b', 'c', 'd'])
        except TypeError, e:
            self.assertEquals("string indices must be integers, not str (on accessing ['a', 'b', 'c', 'd'] in {'a': {'b': {'c': 'X'}}})", str(e))
        else: self.fail()

        # index in list
        self.assertEquals('a', get_in(['a', 'b'], [0]))
        self.assertEquals('not-found', get_in(['a', 'b'], [3], default='not-found'))
        self.assertEquals('c', get_in({'a': ['b', 'c']}, ['a', 1]))
        try:
            self.assertEquals('c', get_in({'a': ['b', 'c']}, ['a', 'b']))
        except TypeError, e:
            self.assertEquals("list indices must be integers, not str (on accessing ['a', 'b'] in {'a': ['b', 'c']})", str(e))
        else: self.fail()

    def testUpdate_in_oldValue(self):
        # No old-value
        log = []
        self.assertEquals({'a': 'x'}, update_in({}, ['a'], lambda o: (log.append(o) or 'x')))
        self.assertEquals([None], log)

        # None old-value
        log = []
        self.assertEquals({'a': 'x'}, update_in({'a': None}, ['a'], lambda o: (log.append(o) or 'x')))
        self.assertEquals([None], log)

        # Some old-value
        log = []
        self.assertEquals({'a': 'x'}, update_in({'a': 'old'}, ['a'], lambda o: (log.append(o) or 'x')))
        self.assertEquals(['old'], log)
        log = []
        self.assertEquals({'a': 'x'}, update_in({'a': {'nested': ['old']}}, ['a'], lambda o: (log.append(o) or 'x')))
        self.assertEquals([{'nested': ['old']}], log)

        # Deeper nested - no old
        log = []
        self.assertEquals({'a': {'b': {'c': 'new', 'z': 'zz'}}}, update_in({'a': {'b': {'z': 'zz'}}}, ['a', 'b', 'c'], lambda o: (log.append(o) or 'new')))
        self.assertEquals([None], log)

        # Deeper nested - old
        log = []
        self.assertEquals({'a': {'b': {'c': 'new'}}}, update_in({'a': {'b': {'c': 'old'}}}, ['a', 'b', 'c'], lambda o: (log.append(o) or 'new')))
        self.assertEquals(['old'], log)

    def testUpdate_in_moreArgs(self):
        # Deeper nested - no old, 1 extra args
        log = []
        self.assertEquals(
            {'a': {'b': {'c': 'new', 'z': 'zz'}}},
            update_in({'a': {'b': {'z': 'zz'}}}, ['a', 'b', 'c'], lambda o, *args: (log.append((o, args)) or 'new'), 2))
        self.assertEquals([(None, (2,))], log)

        # Deeper nested - old, n-extra args
        log = []
        self.assertEquals({'a': {'b': {'c': 'new'}}}, update_in({'a': {'b': {'c': 'old'}}}, ['a', 'b', 'c'], lambda o, *args: (log.append((o, args)) or 'new'), 2, 3, 4))
        self.assertEquals([('old', (2, 3, 4))], log)

    def testUpdate_in_when(self):
        # implementation uses get_in and assoc_in; so only testing conditional-intermediate dict creation and value-updating.

        # basic-update-in works
        self.assertEquals({'k': (None, 'new')}, update_in_when({}, ['k'], lambda old: (old, 'new')))
        self.assertEquals({'k': ('old', 'new')}, update_in_when({'k': 'old'}, ['k'], lambda old: (old, 'new')))
        self.assertEquals({'k': ('old', 'new')}, update_in_when({'k': 'old'}, ['k'], lambda old, m, a: self.assertEquals('more', m) or self.assertEquals('args', a) or (old, 'new'), 'more', 'args'))
        self.assertEquals({'a': {'b': {'c': 'd'}}}, update_in_when({'a': {}}, ['a', 'b', 'c'], lambda old: 'd'))

        # value not updated if condition / f-retval is None
        self.assertEquals({'k': 'old'}, update_in_when({'k': 'old'}, ['k'], lambda old: None))

        # intermediate-dicts not created if condition / f-retval is None
        self.assertEquals({'a': {}}, update_in_when({'a': {}}, ['a', 'b', 'c'], lambda old: None))

    def testAssoc(self):
        self.assertEquals({'k': 'v'}, assoc({}, 'k', 'v'))
        self.assertEquals({'k': [{tuple()}]}, assoc({}, 'k', [{tuple()}]))
        self.assertEquals({'k': 'v2'}, assoc({'k': 'v'}, 'k', 'v2'))
        self.assertEquals({'k': 'v', 'a': 'b', 'x': 'y'}, assoc({'k': 'v'}, 'a', 'b', 'x', 'y'))

        self.assertRaises(TypeError, lambda: assoc({}, 'k'))
        try:
            assoc({}, 'k', 'v', 'a')
            self.fail()
        except TypeError, e:
            self.assertEquals('Uneven number of kvs', str(e))

        self.assertRaises(TypeError, lambda: assoc({}, 'k', 'v', 'a', 'v', 'b'))

    def testAssoc_when(self):
        self.assertEquals({}, assoc_when({}, 'x', None))
        self.assertEquals({'x': False}, assoc_when({}, 'x', False))
        self.assertEquals({'x': False}, assoc_when({}, 'x', 0))
        self.assertEquals({'z': []}, assoc_when({}, 'z', []))
        self.assertEquals({'x': 'z'}, assoc_when({}, 'x', 'z'))

    def testAssoc_in_emptyDict(self):
        self.assertEquals({'a': 'v'}, assoc_in({}, keypath=['a'], v='v'))
        self.assertEquals({'a': {'b': 'v'}}, assoc_in({}, ['a', 'b'], 'v'))
        self.assertEquals({'a': {'b': {'c': 'v'}}}, assoc_in({}, ['a', 'b', 'c'], 'v'))

    def testAssoc_in_disjointDict(self):
        self.assertEquals(
            {'a': 'v', 'z': ['what', 'ever']},
            assoc_in({'z': ['what', 'ever']}, keypath=['a'], v='v'))
        self.assertEquals(
            {'a': {'b': 'v'}, 'z': 'x'},
            assoc_in({'z': 'x'}, ['a', 'b'], 'v'))

    def testAssoc_in_overlapDict(self):
        self.assertEquals(
            {'a': {'b': 'v'}},
            assoc_in({'a': {}}, ['a', 'b'], 'v'))
        self.assertEquals(
            {'a': {'b': 'v', 'z': 'x'}},
            assoc_in({'a': {'z': 'x'}}, ['a', 'b'], 'v'))
        self.assertEquals(
            {'a': {'b': {'c': 'v'}}},
            assoc_in({'a': {}}, ['a', 'b', 'c'], 'v'))
        self.assertEquals(
            {'a': {'b': {'c': 'v', 'z': 'zz'},
                   'y': 'yy'},
             'x': 'xx'},
            assoc_in(
                {
                    'a': {'b': {'z': 'zz'},
                          'y': 'yy'},
                    'x': 'xx',
                }, ['a', 'b', 'c'], 'v'))

    def testAssoc_in_overwriteVal(self):
        self.assertEquals(
            {'a': 'v'},
            assoc_in({'a': 'will-be-overwritten'}, ['a'], 'v'))
        self.assertEquals(
            {'a': 'v'},
            assoc_in({'a': {'nested': 'val'}}, ['a'], 'v'))
        self.assertEquals(
            {'a': 'v'},
            assoc_in({'a': ['nested', 'val']}, ['a'], 'v'))
        self.assertEquals(
            {'a': {'b': 'NEW',
                   'y': 'yy'},
             'x': 'xx'},
            assoc_in(
                {
                    'a': {'b': 'NEW',
                          'y': 'yy'},
                    'x': 'xx',
                }, ['a', 'b'], 'NEW'))

    def testAssoc_in_pathAcrossNonDicts(self):
        try:
            assoc_in({'a': 'no-dict'}, ['a', 'b'], 'v')
        except ValueError, e:
            self.assertEquals("At path ['a'] value 'no-dict' is not a dict.", str(e))
        else: self.fail()

        try:
            assoc_in({'a': 'no-dict'}, ['a', 'b', 'c'], 'v')
        except ValueError, e:
            self.assertEquals("At path ['a'] value 'no-dict' is not a dict.", str(e))
        else: self.fail()

        try:
            assoc_in({'a': {'b': 'no-dict'}}, ['a', 'b', 'c'], 'v')
        except ValueError, e:
            self.assertEquals("At path ['a', 'b'] value 'no-dict' is not a dict.", str(e))
        else: self.fail()

    def testAssoc_in_when(self):
        self.assertEquals({}, assoc_in_when({}, ['x', 'y'], None))
        self.assertEquals({'x': {'y': False}}, assoc_in_when({}, ['x', 'y'], False))
        self.assertEquals({'x': {'y': 'z'}}, assoc_in_when({}, ['x', 'y'], 'z'))

    def testTrampoline(self):
        # Looks like fn application when fn return a non-fn
        self.assertEquals('x', trampoline(identity, 'x'))
        self.assertRaises(TypeError, lambda: trampoline(identity, 'x', 'y'))

        # Calls fn (0-arity) if retval is a fn
        self.assertEquals(('out', 'in', 'put'), trampoline(lambda _in, put: lambda: ('out', _in, put), 'in', 'put'))

        # Keeps doing that until retval is not a fn
        def mutual_recursion_until(stopNr, log):
            def a(n):
                (log is not None) and log.append(n)
                if n >= stopNr:
                    return n
                return lambda: b(n + 1)

            def b(n):
                (log is not None) and log.append(n)
                return lambda: a(n + 1)
            return a, b, log

        a, b, log = mutual_recursion_until(10, [])
        self.assertEquals(10, trampoline(a, 0))
        self.assertEquals(11, len(log))
        self.assertEquals([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], log)

        a, b, log = mutual_recursion_until(1002, None)
        self.assertEquals(1002, trampoline(a, 0))
        self.assertEquals(None, log)

        # Mutual recursion without a trampoline #fail - because of missing TCO in Python.
        def mutual_recursion_until_noTrampoline(stopNr):
            def a(n):
                if n >= stopNr:
                    return n
                return b(n + 1)
            def b(n):
                return a(n + 1)
            return a, b

        a, b = mutual_recursion_until_noTrampoline(10)
        self.assertEquals(10, a(0))

        a, b = mutual_recursion_until_noTrampoline(1002)
        self.assertRaises(RuntimeError, lambda: a(0))

    def testBefore(self):
        log = []
        def f(*a, **kw):
            log.append(['f', a, kw])
            return ['f', a, kw]

        def g(*a, **kw):
            log.append(['g', a, kw])
            return ['g', a, kw]

        g_before_f = before(f, g)
        args = [(1,), {'k': 'v'}]
        self.assertEquals(append(['f'], *args), g_before_f(1, k='v'))
        self.assertEquals([append(['g'], *args), append(['f'], *args)], log)

        # 2nd time -> called again
        del log[:]
        self.assertEquals(append(['f'], *args), g_before_f(1, k='v'))
        self.assertEquals([append(['g'], *args), append(['f'], *args)], log)

        # No args ok too
        del log[:]
        self.assertEquals(['f', (), {}], g_before_f())
        self.assertEquals([['g', (), {}], ['f', (), {}]], log)

        # before fn (g) only called for side-effects; retval ignored
        def g(*a, **kw):
            log.append(['g', a, kw])
            return 'IGNORED'

        del log[:]
        g_before_f = before(f, g)
        self.assertEquals(append(['f'], *args), g_before_f(1, k='v'))
        self.assertEquals([append(['g'], *args), append(['f'], *args)], log)

    def test_after(self):
        log = []
        def f(*a, **kw):
            log.append(['f', a, kw])
            return ['f', a, kw]

        def g(*a, **kw):
            log.append(['g', a, kw])
            return ['g', a, kw]

        g_after_f = after(f, g)
        args = [(1,), {'k': 'v'}]
        self.assertEquals(append(['f'], *args), g_after_f(1, k='v'))
        self.assertEquals([append(['f'], *args), append(['g'], *args)], log)

        # 2nd time -> called again
        del log[:]
        self.assertEquals(append(['f'], *args), g_after_f(1, k='v'))
        self.assertEquals([append(['f'], *args), append(['g'], *args)], log)

        # No args ok too
        del log[:]
        self.assertEquals(['f', (), {}], g_after_f())
        self.assertEquals([['f', (), {}], ['g', (), {}]], log)

        # after fn (g) only called for side-effects; retval ignored
        def g(*a, **kw):
            log.append(['g', a, kw])
            return 'IGNORED'

        del log[:]
        g_after_f = after(f, g)
        self.assertEquals(append(['f'], *args), g_after_f(1, k='v'))
        self.assertEquals([append(['f'], *args), append(['g'], *args)], log)

    def test_append(self):
        self.assertRaises(AttributeError, lambda: append(object()).append('x'))
        self.assertRaises(AttributeError, lambda: append(object(), 'x'))

        # 0-arity -> new list
        self.assertEquals([], append())
        self.assertFalse(append() is append()) # New list every o-arity invocation.

        # 1-arity input == output
        in_empty = []
        in_12 = [1, 2]
        self.assertEquals([], append(in_empty))
        self.assertTrue(in_empty is append(in_empty))
        self.assertEquals([1, 2], append(in_12))
        self.assertTrue(in_12 is append(in_12))
        o = object()            # not append-able
        self.assertTrue(o is append(o))

        # n-arity
        in_a = ['a']
        res = append(in_a, 'b')
        self.assertEquals(['a', 'b'], res)
        self.assertTrue(in_a is res) # Mutable type (expected & required for `append').
        res = append(in_a, 'c', 'd')
        self.assertEquals(['a', 'b', 'c', 'd'], res)
        self.assertTrue(in_a is res)
        res = append(append(in_empty, 1, 2), 3)
        self.assertEquals([1, 2, 3], res)
        self.assertTrue(in_empty is res)

        # with 2-n args being None
        self.assertEquals([None], append(None, None))
        self.assertEquals([None], append([], None))
        self.assertEquals([1, 2, None], append([1, 2], None))
        self.assertEquals([1, 2, None, None], append([1, 2], None, None))

    def test_strng(self):
        class A(object):
            def __str__(self):
                return 'yes'
            def __repr__(self):
                return 'no'

        # 0-arity
        self.assertEquals("", strng())

        # 1-arity
        self.assertEquals("", strng(None))
        self.assertEquals("False", strng(False)) # Pointless, but proves the point
        self.assertEquals("", strng(""))
        self.assertEquals("xx", strng("xx"))
        self.assertEquals("xx", strng(u"xx"))
        self.assertEquals("yes", strng(A()))

        # n-arity
        self.assertEquals("", strng(None, None))
        self.assertEquals("", strng(None, None, None))
        self.assertEquals("", strng("", "", ""))
        self.assertEquals("aap, noot en mies.", strng("a", "ap", ", noot", " en mies."))
        self.assertEquals("yesyesyes", strng(A(), None, A(), None, A()))

    def testJuxt(self):
        log = []
        def fn_fn(id, retval):
            def a_fn(*a, **kw):
                log.append((id, a, kw))
                return retval
            return a_fn

        # No fns
        self.assertEquals([], juxt()())
        self.assertEquals([], juxt()('arg1', 'arg2', kw='kwarg1'))

        # 1 fn
        _1 = fn_fn('1', 'rv-1')
        self.assertEquals(['rv-1'], juxt(_1)('a1', kw='kw1'))
        self.assertEquals([('1', ('a1',), {'kw': 'kw1'})], log)

        log = []
        # n-fns
        _1 = fn_fn(1, [1, {}, set()])
        _2 = fn_fn(2, 'rv-2')
        _3 = fn_fn(3, ('stuff',))
        j_fn = juxt(_1, _2, _3)
        self.assertEquals([[1, {}, set()], 'rv-2', ('stuff',)], j_fn('a1', 2, kw='kw1', k3=3)) # in-order retvals
        self.assertEquals(      # in-order called
            [(1, ('a1', 2), {'k3': 3, 'kw': 'kw1'}),
             (2, ('a1', 2), {'k3': 3, 'kw': 'kw1'}),
             (3, ('a1', 2), {'k3': 3, 'kw': 'kw1'}),],
            log)

        # called again
        log = []
        self.assertEquals([[1, {}, set()], 'rv-2', ('stuff',)], j_fn())
        self.assertEquals(      # in-order called
            [(1, (), {}),
             (2, (), {}),
             (3, (), {}),],
            log)

    def testSome_thread(self):
        def input_is(f, expected_val):
            def _input_is(v):
                self.assertEquals(expected_val, v)
                return f(v)
            return _input_is

        def raiser(v):
            raise RuntimeError('should not happen!')

        self.assertEquals(None, some_thread(None))
        self.assertEquals('x', some_thread('x'))
        self.assertEquals(None, some_thread(None, raiser))
        self.assertRaises(RuntimeError, lambda: some_thread('x', raiser))
        self.assertEquals(42, some_thread('x', input_is(lambda x: 42, 'x')))
        self.assertEquals(42, some_thread('x',
                                          input_is(lambda x: 'y', 'x'),
                                          input_is(lambda x: 42, 'y')))
        self.assertEquals(None, some_thread('x',
                                          input_is(lambda x: None, 'x'),
                                          raiser))

        # Example usage:
        self.assertEqual(None, some_thread(5,
                                           lambda x: x + 3,
                                           lambda x: None, # Some either-a-number-or-None fn
                                           lambda x: x + 5))

    def testFpartial(self):
        f = lambda *a, **kw: (a, kw)
        self.assertRaises(TypeError, lambda: fpartial(f)())
        self.assertEquals((('a',), {}), fpartial(f)('a'))
        self.assertEquals(((1,), {}), fpartial(f)(1))
        self.assertEquals(((1, 'a', 'b'), {}), fpartial(f, 'a', 'b')(1))
        self.assertEquals(((1,), {"k1": "w1", "k2": "w2"}), fpartial(f, k1="w1", k2="w2")(1))
        self.assertEquals(((1, "a1"), {"k1": "w1"}), fpartial(f, "a1", k1="w1")(1))

    def testComp(self):
        # comp(osition) algoritm shamelessly stolen from Clojure & translated to the simplest possible Pythonic equavalent.
        # 0-arity -> identity
        o = object()
        f = comp()
        self.assertEquals("x", f("x"))
        self.assertEquals({}, f({}))
        self.assertEquals("x", comp()("x"))
        self.assertTrue(o is comp()(o))

        # 1-arity -> in-fn is out-fn
        fn_a = lambda x, y, z: x + y + z
        self.assertEquals(6, fn_a(1, 2, 3))
        self.assertEquals(6, comp(fn_a)(1, 2, 3))
        self.assertTrue(fn_a is comp(fn_a))

        # 2-arity -> new fn taking any-(kw)args: rhs-fn called-with: all-args, lhs-fn result of rhs-call, lhs-result returned
        fn_lhs = lambda x: x * 5
        fn_rhs = lambda x, y, z: x + y + z
        fn_2 = comp(fn_lhs, fn_rhs)
        self.assertEquals(30, fn_2(1, 2, 3))
        self.assertEquals(15, fn_2(1, 1, 1))

        # 3..n arity -> recusive-called 2-arities
        #   - rightmost fn called with all original args to composed fn
        #   - all others right-to-left passed the intermediate result of their right-neighbour
        fn_l = lambda x: x ** 3
        fn_m = lambda x: 2 * x
        fn_r = lambda x, kw: x + kw
        fn_3 = comp(fn_l, fn_m, fn_r)
        self.assertEquals(1000, fn_3(2, kw=3))

        # n
        fn_pl1 = lambda x: x + 1
        fn_n = comp(fn_pl1, fn_pl1, fn_pl1, fn_pl1, fn_pl1)
        self.assertEquals(5, fn_n(0))

    def test_reduced(self):
        r = reduced("val")
        self.assertEquals(reduced, type(r))
        self.assertEquals("val", reduced(r).val.val) # DO NOT DO THIS!
        self.assertEquals(True, is_reduced(r))
        self.assertEquals("val", r.val)
        self.assertEquals("val", unreduced(r))
        self.assertEquals("val", unreduced(unreduced(r)))
        self.assertEquals("val2", unreduced("val2"))
        self.assertEquals(True, is_reduced(ensure_reduced(r)))
        self.assertEquals("val", ensure_reduced(r).val)
        self.assertEquals("val", unreduced(ensure_reduced(r)))
        self.assertEquals("val", unreduced(ensure_reduced(ensure_reduced(r))))

    def test_local_reduce_implementation_reduced(self):
        def make_rf():
            until = []
            def add_3_things(acc, x):
                acc = acc + x
                until.append(True)
                if len(until) == 3:
                    return ensure_reduced(acc)
                return acc
            return add_3_things

        x = reduce(make_rf(), 0, [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEquals(6, x)
        self.assertFalse(is_reduced(x))

    def test_local_reduce_implementation_arity2_emptyColl(self):
        def f():
            return 'x'
        self.assertEquals('x', reduce(f, []))

    def test_local_reduce_implementation_arity2_coll_1_item(self):
        def f():
            raise Hell
        self.assertEquals(1, reduce(f, [1]))

    def test_local_reduce_implementation_arity2_coll_2_item(self):
        def f(acc, e):
            return acc + e
        self.assertEquals(3, reduce(f, [1, 2]))

    def test_local_reduce_implementation_arity2_coll_n_item(self):
        def f(acc, e):
            return acc + e
        self.assertEquals(10, reduce(f, [1, 2, 3, 4]))

    def test_local_reduce_implementation_arity3_emptyColl(self):
        def f(acc, e):
            raise Hell
        self.assertEquals('x', reduce(f, 'x', []))

    def test_local_reduce_implementation_arity3_coll_1_item(self):
        def f(acc, e):
            return acc + e
        self.assertEquals(3, reduce(f, 1, [2]))

    def test_local_reduce_implementation_arity3_coll_2_item(self):
        def f(acc, e):
            return acc + e
        self.assertEquals(6, reduce(f, 1, [2, 3]))

    def test_local_reduce_implementation_arity3_coll_n_item(self):
        def f(acc, e):
            return acc + e
        self.assertEquals(15, reduce(f, 1, [2, 3, 4, 5]))

    def test_local_reduce_bad_arity(self):
        self.assertRaises(TypeError, lambda: reduce(lambda:None)) # Too few
        self.assertRaises(TypeError, lambda: reduce(lambda:None, 1, [2], 'drie')) # Too many

    def testRun(self):
        log = []
        f = lambda i: log.append(i)

        self.assertEquals(None, run(f, []))
        self.assertEquals([], log)

        self.assertEquals(None, run(f, [1, 2, 3]))
        self.assertEquals([1, 2, 3], log)

    def test_completing(self):
        def rf1(acc=None, e=None):
            if acc == e == None:
                return 0       # Some empty-coll stuffs

            assert acc and e    # either 2-arity or 0-arity, never 1-arity-called
            return acc + e      # Some reducing functionality

        def rf2(acc=None, e=None):
            if acc == e == None:
                return 'hi!'

            assert acc and e
            return 'there'

        c_f1 = completing(rf1)
        c_f2 = completing(rf2)

        # 0-arity (calls original-fn)
        self.assertEquals(0, c_f1())
        self.assertEquals('hi!', c_f2())

        # 1-arity (default impl -> identity)
        self.assertEquals(42, c_f1(42))
        self.assertEquals('whatever', c_f1('whatever'))
        d = {'no': 'matter', 'what': 'in-is-out'}
        self.assertTrue(d is c_f2(d))

        # 2-arity (calls original-fn)
        self.assertEquals(44, c_f1(42, 2))
        self.assertEquals('there', c_f2('in', 'put'))

        # 1-arity (given cf-fn)
        cf_1 = lambda x: [x, 'cf']
        cf_2 = lambda x: list(x)
        c_f1_cf1 = completing(rf1, cf_1)
        c_f2_cf2 = completing(rf2, cf_2)
        self.assertEquals([42, 'cf'], c_f1_cf1(42))
        self.assertEquals(['in', 'put'], c_f2_cf2(('in', 'put')))

        # Bad arity
        self.assertRaises(TypeError, lambda: completing(rf1)(1, 2, 3))

    def test_transduce(self):
        def rf1(acc=None, e=None):
            if acc == e == None:
                return []

            assert (acc is not None) and (e is not None)
            acc.append(e + 10)       # Assuming acc is a list.
            return acc

        # With identity i.s.o. a (composed) transducer(s) - works just like reduce, except for the 1-arity call to `f'.
        self.assertEquals(10, transduce(identity, completing(lambda acc, e: acc + e), 1, [2, 3, 4]))
        self.assertEquals([11, 12, 13, 14], transduce(identity, completing(rf1), [1, 2, 3, 4]))

        # With one transducer
        def _a(acc, e):
            acc.append(e)
            return acc
        self.assertEquals([1, 2], transduce(take(2), completing(_a), [], [1, 2, 3, 4, 5]))

        # With more transducers (composed)
        self.assertEquals([11, 11, 12, 12, 13, 13], transduce(
            comp(
                take(3),
                map(lambda x: x + 10),
                map(lambda x: '\t\n\r{}-{}   '.format(x, x)),
                map(lambda x: split(x, '-')),
                cat,
                map(lambda x: int(strip(x))),
            ),
            completing(_a), [], [1, 2, 3, 4, 5]))

    def test_map_xf(self):
        # 0-arity
        called = []
        self.assertEquals('x', map(lambda: Hell)(lambda: called.append(True) or 'x')())
        self.assertEquals([True], called)

        # 1-arity
        called = []
        self.assertEquals('x', map(lambda: Hell)(lambda r: called.append(r) or 'x')('res'))
        self.assertEquals(['res'], called)

        # 2-arity
        called = []
        self.assertEquals('res', map(lambda x: x + 1)(lambda r, i: called.append((r, i)) or 'res')('in', 1))
        self.assertEquals([('in', 2)], called)

        # 3+-arity
        called = []
        self.assertEquals('res', map(lambda x, y, z: x + y + z)(lambda r, i: called.append((r, i)) or 'res')('in', 1, 2, 3))
        self.assertEquals([('in', 6)], called)

        # with transduce
        self.assertEquals(27, transduce(map(lambda x: x + 10), completing(lambda acc, e: acc + e), 0, [5, 2]))

    def test_map_1coll(self):
        # TODO: test lazyness when implemented (using lazy_seq)!
        plus = lambda x: x + 1
        l = list

        # empty coll - fn not called
        self.assertEquals([], l(map(raiser, [])))

        # 1-item
        self.assertEquals([2], l(map(plus, [1])))
        # 2-item
        self.assertEquals([2, 3], l(map(plus, [1, 2])))
        # n-item
        self.assertEquals([11, 12, 13, 14], l(map(plus, [10, 11, 12, 13])))

    def test_map_Ncoll(self):
        # TODO: test lazyness when implemented (using lazy_seq)!
        plus = lambda _1, *a: plus(_1 + first(a), *a[1:]) if a else _1
        l = list

        # empty coll - fn not called
        self.assertEquals([], l(map(raiser, [], [], [])))

        # 1-item
        self.assertEquals([2], l(map(plus, [1], [1, 99, 100, 101])))
        # 2-item
        self.assertEquals([1, 2], l(map(plus, [0, 0], [1, 2])))
        # n-item
        self.assertEquals([12, 13, 14, 15], l(map(plus, [1, 2, 3, 4], [4, 3, 2, 1], [7, 8, 9, 10])))
        self.assertEquals([12, 13, 14, 15], l(map(plus, [1, 2, 3, 4], [4, 3, 2, 1, 'x', object()], [7, 8, 9, 10, None, None])))

    def test_filter_xf(self):
        assert_tx_default_0_1_arities(filter(raiser))
        assert_tx_default_bad_arity(filter(raiser))

        # 2-arity - not-filtered
        called = []
        self.assertEquals('res', filter(lambda x: x == 1)(lambda r, i: called.append((r, i)) or 'res')('in', 1))
        self.assertEquals([('in', 1)], called)

        # 2-arity - filtered
        called = []
        self.assertEquals('in', filter(lambda x: x != 1)(lambda r, i: called.append((r, i)) or 'res')('in', 1))
        self.assertEquals([], called)

        # with transduce
        self.assertEquals(4, transduce(filter(lambda x: (x % 2) == 1), completing(lambda acc, e: acc + e), 0, [1, 2, 3, 4]))

    def test_remove_xf(self):
        assert_tx_default_0_1_arities(remove(raiser))
        assert_tx_default_bad_arity(remove(raiser))

        # 2-arity - not-removed
        called = []
        self.assertEquals('res', remove(lambda x: x != 1)(lambda r, i: called.append((r, i)) or 'res')('in', 1))
        self.assertEquals([('in', 1)], called)

        # 2-arity - removed
        called = []
        self.assertEquals('in', remove(lambda x: x == 1)(lambda r, i: called.append((r, i)) or 'res')('in', 1))
        self.assertEquals([], called)

        # with transduce
        self.assertEquals(4, transduce(remove(lambda x: (x % 2) == 0), completing(lambda acc, e: acc + e), 0, [1, 2, 3, 4]))

    def test_iterate(self):
        i = iterate(lambda s: s+'x', '')
        self.assertEquals('', next(i))
        self.assertEquals('x', next(i))
        self.assertEquals('xx', next(i))
        self.assertEquals('xxx', next(i))

        i = iterate(lambda n: n + 1, 3)
        self.assertEquals(3, next(i))
        self.assertEquals(4, next(i))

    def test_interleave(self):
        l = list

        # empty
        self.assertEquals([], l(interleave()))
        self.assertEquals([], l(interleave([])))
        self.assertEquals([], l(interleave([], [])))

        # interleave
        self.assertEquals([1, 'a', 2, 'b', 3, 'c'], l(interleave([1, 2, 3], ['a', 'b', 'c'])))

        # shortest
        self.assertEquals([1, 'a', 2, 'b'], l(interleave([1, 2, 3], ['a', 'b'])))
        self.assertEquals([], l(interleave([], [1, 2, 3], ['a', 'b'])))

    def test_complement(self):
        called = []
        def f_0_true():
            called.append(('f_0_true',))
            return 42
        def f_0_false():
            called.append(('f_0_false',))
            return False
        def f_1_true(a):
            called.append(('f_1_true', a))
            return 'true'
        def f_n_false(a, b, c, k='v1', k2='v2'):
            called.append(('f_n_false', a, b, c, k, k2))
            return ''

        def t(f, *a, **kw):
            ret = complement(f)(*a, **kw)
            _called = called[:]
            self.assertEquals(1, len(_called))
            del called[:]
            return (ret, _called[0])

        self.assertRaises(TypeError, lambda: t(f_0_true, 'too-many-args'))
        self.assertRaises(TypeError, lambda: t(f_0_true, kw='too-many-kwargs'))
        self.assertRaises(TypeError, lambda: t(f_1_true))

        self.assertEquals((False, ('f_0_true',)), t(f_0_true))
        self.assertEquals((True, ('f_0_false',)), t(f_0_false))
        self.assertEquals((False, ('f_1_true', 'x')), t(f_1_true, 'x'))
        self.assertEquals((True, ('f_n_false', 1, 'B', object, 'v1', 'K2')), t(f_n_false, 1, 'B', object, k2='K2'))

    def test_cat(self):
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
        f = test_f('whatever')
        self.assertEquals('whatever', cat(f)())
        self.assertEquals([()], log())

        # 1-arity
        f = test_f('whatever-done')
        self.assertEquals('whatever-done', cat(f)('whatever-in'))
        self.assertEquals([('whatever-in',)], log())

        # 2-arity - nested empty (result-in == result=out, rf not called)
        f = test_f('whatever')
        self.assertEquals('whatever-in', cat(f)('whatever-in', []))
        self.assertEquals([], log())

        # 2-arity - nested 1
        f = test_f('whatever')
        self.assertEquals('whatever', cat(f)('whatever-in', [1]))
        self.assertEquals([('whatever-in', 1)], log())

        # 2-arity - nested n
        f = test_f('whatever')
        self.assertEquals('whatever', cat(f)('whatever-in', [1, 2, 3, 4]))
        self.assertEquals([
            ('whatever-in', 1),
            ('whatever', 2),    # 2-n acc is result of the prev. call
            ('whatever', 3),
            ('whatever', 4),
        ], log())

        # 2-arity - nested has reduced value - 1
        def test_f_2(n):
            def f(acc, e):
                _log.append((acc, e))
                r = '{}-{}'.format(acc, e)
                if e == n:
                    return reduced('{}-done'.format(r))
                return r
            return f

        f = test_f_2(1)
        r = cat(f)('whatever-in', [1, 2, 3, 4])
        self.assertTrue(is_reduced(r))
        self.assertEquals('whatever-in-1-done', r.val)
        self.assertEquals([
            ('whatever-in', 1),
        ], log())

        # 2-arity - nested has reduced value - n
        f = test_f_2(3)
        r = cat(f)('whatever-in', [1, 2, 3, 4])
        self.assertTrue(is_reduced(r))
        self.assertEquals('whatever-in-1-2-3-done', r.val)
        self.assertEquals([
            ('whatever-in', 1),
            ('whatever-in-1', 2),
            ('whatever-in-1-2', 3),
        ], log())

        # bad arity
        self.assertRaises(TypeError, lambda: cat(None, None, None))

        # with transduce
        def _a(acc, e):
            acc.append(e)
            return acc
        self.assertEquals([1, 2, 3, 4, 5, 6], transduce(cat, completing(_a), [], [[1, 2], [3, 4, 5], [], [6]]))

    def test_take(self):
        l = list

        # 2-arity
        self.assertEquals([], l(take(15, [])))
        self.assertEquals([], l(take(0, [1, 2])))
        self.assertEquals([], l(take(-12, [1, 2]))) # Ridiculous, but fine.
        self.assertEquals([1, 2], l(take(15, [1, 2])))
        self.assertEquals([1, 2], l(take(3, [1, 2])))
        self.assertEquals([1, 2, 3], l(take(3, [1, 2, 3])))
        self.assertEquals([1, 2, 3], l(take(3, [1, 2, 3, 4])))
        self.assertEquals([1, 2, 3], l(take(3, [1, 2, 3, 4, 5])))

        # 1-arity (transducer)
        _log = []
        def log():
            _l = _log[:]
            del _log[:]
            return _l

        def next_xf(*a):
            assert 0 <= len(a) <= 2
            _log.append(a)
            if len(a) == 0:
                return []
            elif len(a) == 1:
                return first(a)
            elif len(a) == 2:
                result_copy = first(a)[:]
                result_copy.append(second(a))
                return result_copy


        # Without 0-arity call (this is *normal*)!
        xf_prestart = take(2)
        xf = xf_prestart(next_xf)

        r = xf([], 1)
        self.assertEquals([([], 1)], log())
        self.assertEquals([1], r)
        r = xf([1], 2)
        self.assertEquals([([1], 2)], log())
        self.assertTrue(is_reduced(r))
        self.assertEquals([1, 2], unreduced(r))
        r = xf(unreduced(r))
        self.assertEquals([([1, 2],)], log())
        self.assertEquals([1, 2], r)

        # With 0-arity call (this is *abnormal*)!
        xf_prestart = take(2)
        xf = xf_prestart(next_xf)

        r = xf()
        self.assertEquals([()], log())
        self.assertEquals([], r)
        r = xf(r, 1)
        self.assertEquals([([], 1)], log())
        self.assertEquals([1], r)
        r = xf([1], 2)
        self.assertEquals([([1], 2)], log())
        self.assertTrue(is_reduced(r))
        self.assertEquals([1, 2], unreduced(r))
        r = xf(unreduced(r))
        self.assertEquals([([1, 2],)], log())
        self.assertEquals([1, 2], r)

        # Using transduce
        def _a(acc, e):
            acc.append(e)
            return acc
        self.assertEquals([1, 2], transduce(take(2), completing(_a), [], [1, 2, 3, 4, 5]))

    def test_interpose(self):
        self.assertRaises(TypeError, lambda: interpose()) # sep(arator) required.
        assert_tx_default_0_1_arities(interpose('-'))
        assert_tx_default_bad_arity(interpose('-'))

        # 2-arity - initial
        _called = []
        def log(r, i):
            append(_called, (r, i))
        def called():
            c = _called[:]
            del _called[:]
            return c

        ip = interpose('-')
        rf = before(lambda r, i: 'res', log)
        xf = ip(rf)             # stateful xf from here!
        # 1st val (in == out)
        self.assertEquals('res', xf('in', 'str'))
        self.assertEquals([('in', 'str')], called())
        # 2nd..n val (prepend interposed sep)
        self.assertEquals('res', xf('in', 'in'))
        self.assertEquals([('in', '-'), ('res', 'in')], called())
        self.assertEquals('res', xf('in', 'g'))
        self.assertEquals([('in', '-'), ('res', 'g')], called())

        # next stateful xf -> initial not sep-prepended.
        xf = ip(rf)
        self.assertEquals('res', xf('in', 'a'))
        self.assertEquals('res', xf('in', 'b'))
        self.assertEquals('res', xf('in', 'c'))
        self.assertEquals(['a', '-', 'b', '-', 'c'], list(map(second, called())))

        # reduced handled ok - initial
        ip = interpose(('thing'))
        rf = before(lambda r, i: reduced('rres'), log)
        xf = ip(rf)
        ret = xf('in', 'a')
        self.assertTrue(is_reduced(ret))
        self.assertEquals('rres', unreduced(ret))
        self.assertEquals([('in', 'a')], called())

        # reduced handled ok - 2nd..n
        _2nd = []
        rf = before(lambda r, i: reduced('rres') if _2nd else (_2nd.append(True) or 'res'), log)
        xf = ip(rf)
        self.assertEquals('res', xf('in', 'a'))
        self.assertEquals([('in', 'a')], called())
        ret = xf('in', 'b')
        self.assertTrue(is_reduced(ret))
        self.assertEquals('rres', unreduced(ret))
        self.assertEquals([('in', ('thing'))], called())

        # with transduce
        self.assertEquals('one', transduce(interpose('~>'), completing(strng), '', ['one']))
        self.assertEquals('initial:one', transduce(interpose('~>'), completing(strng), 'initial:', ['one']))
        self.assertEquals('one~>two~>three', transduce(interpose('~>'), completing(strng), '', ['one', 'two', 'three']))
        self.assertEquals('initial:one~>two~>three', transduce(interpose('~>'), completing(strng), 'initial:', ['one', 'two', 'three']))
        self.assertEquals('initial:one~>', transduce(comp(interpose('~>'), take(2)), completing(strng), 'initial:', ['one', 'two', 'three']))

    def test_sequence(self):
        _log = []
        def log():
            l = _log[:]
            del _log[:]
            return l

        class log_iter(object):
            def __init__(self, in_):
                self._iterrable = iter(in_)
            def __iter__(self):
                return self
            def next(self):
                try:
                    v = self._iterrable.next()
                except StopIteration:
                    append(_log, 'coll-done')
                    raise
                else:
                    append(_log, v)
                    return v

        def assert_sqnc(expected_res_log, *sequence_args):
            def rf(acc, res_log):
                seq_rest = acc
                exp_res, exp_log = res_log
                res = builtin_next(seq_rest, 's-done')
                self.assertEquals(exp_res, res)
                self.assertEquals(exp_log, log())
                return seq_rest

            if not expected_res_log:
                self.fail('expected_res_log must have >= 1 enties.  End-of-sequence is signaled by "s-done" for sequence-output and "coll-done" for a consumed seq / iterable.')

            if len(sequence_args) == 1:
                init = sequence(log_iter(sequence_args[0]))
            elif len(sequence_args) == 2:
                init = sequence(sequence_args[0], log_iter(sequence_args[1]))
            else:
                self.fail('Unexpected sequence_args')

            return reduce(rf, init, expected_res_log)

        # no xform, empty-coll
        self.assertEquals(GeneratorType, type(sequence(None)))
        self.assertEquals([], l(sequence(None)))
        self.assertEquals([], l(sequence([])))
        self.assertEquals([], l(sequence(())))
        self.assertEquals([], l(sequence(iter(()))))

        # no xform, 1-coll
        self.assertEquals(GeneratorType, type(sequence([1])))
        self.assertEquals([1], l(sequence([1])))
        self.assertEquals([1], l(sequence((1,))))

        # no xform, n-coll
        self.assertEquals(['a', 'b'], l(sequence((x for x in ['a', 'b']))))
        self.assertEquals([1, 2, 3], l(sequence([1, 2, 3])))

        # xform, empty-coll
        self.assertEquals(GeneratorType, type(sequence(take(1), None)))
        self.assertEquals([], l(sequence(take(1), None)))
        self.assertEquals([], l(sequence(take(1), [])))
        self.assertEquals([], l(sequence(take(1), ())))
        self.assertEquals([], l(sequence(take(1), iter(()))))

        # xform, 1-coll
        self.assertEquals(GeneratorType, type(sequence(take(1), [1])))
        self.assertEquals([], l(sequence(take(0), [1])))
        self.assertEquals([], l(sequence(take(0), (1,))))
        self.assertEquals([1], l(sequence(take(1), [1])))
        self.assertEquals([1], l(sequence(take(1), (1,))))

        # xform, n-coll
        self.assertEquals(['a'], l(sequence(take(1), (x for x in ['a', 'b']))))
        self.assertEquals([1, 2], l(sequence(take(3), [1, 2])))
        self.assertEquals([1, 2, 3], l(sequence(take(3), [1, 2, 3])))
        self.assertEquals([1, 2, 3], l(sequence(take(3), [1, 2, 3, 4])))

        # (no-xform) lazy / as-late-as-possible realization of input "coll"
        g_empty = (x for x in [])
        g_1 = (x for x in [1])
        g_n = (x for x in [1, 2, 3])

        assert_sqnc([('s-done', ['coll-done'])], g_empty)
        assert_sqnc([(1, [1]), ('s-done', ['coll-done'])], g_1)
        assert_sqnc([(1, [1]), (2, [2]), (3, [3]), ('s-done', ['coll-done'])], g_n)

        # xform-ed lazy / as-late-as-possible realization of input "coll"
        g_empty_fn = lambda: (x for x in [])
        g_1_fn = lambda: (x for x in [1])
        g_n_fn = lambda: (x for x in [1, 2, 3])

        assert_sqnc([('s-done', ['coll-done'])], take(0), g_empty_fn())
        assert_sqnc([('s-done', ['coll-done'])], take(1), g_empty_fn())
        assert_sqnc([('s-done', [1])], take(0), g_1_fn())
        assert_sqnc([(1, [1]), ('s-done', [])], take(1), g_1_fn())
        assert_sqnc([(1, [1]), ('s-done', ['coll-done'])], take(2), g_1_fn())
        assert_sqnc([(1, [1]), ('s-done', [])], take(1), g_n_fn())
        assert_sqnc([(1, [1]), (2, [2]), ('s-done', [])], take(2), g_n_fn())
        assert_sqnc([(1, [1]), (2, [2]), (3, [3]), ('s-done', [])], take(3), g_n_fn())
        assert_sqnc([(1, [1]), (2, [2]), (3, [3]), ('s-done', ['coll-done'])], take(4), g_n_fn())

        # xform "closing remarks" 1-arity for xf-step called before final buffer-outputs generated.
        def party(rf):
            def _party_step(*a):
                if len(a) == 0:
                    return rf()
                elif len(a) == 1:
                    result, = a
                    self.assertEquals(None, result)
                    rf(result, 'parrr')
                    rf(result, 'ty!')
                    return rf(result)
                else:           # len(a) == 2
                    result, input_ = a
                    return rf(result, input_)
            return _party_step

        self.assertEquals(['parrr', 'ty!'], l(sequence(party, None)))
        self.assertEquals(['parrr', 'ty!'], l(sequence(party, [])))
        self.assertEquals([1, 'parrr', 'ty!'], l(sequence(party, [1])))
        self.assertEquals([1, 2, 'parrr', 'ty!'], l(sequence(party, [1, 2])))
        assert_sqnc([(1, [1]), (2, [2]), ('parrr', []), ('ty!', []), ('s-done', [])], comp(take(2), party), g_n_fn())


def dumbEqual(expected, result, msg=None):
    if expected != result:
        raise AssertionError('{} != {}{}'.format(expected, result, '\nMessage: {}'.format(msg) if msg else ''))

def assert_tx_default_0_1_arities(transducer):
    # 0-arity
    called = []
    dumbEqual('whatever', transducer(lambda: called.append(True) or 'whatever')())
    dumbEqual([True], called)

    # 1-arity
    called = []
    dumbEqual('whatever', transducer(lambda r: called.append(r) or 'whatever')('result-(whatever)'))
    dumbEqual(['result-(whatever)'], called, 'zz-top!')

def assert_tx_default_bad_arity(transducer):
    try:
        transducer(None, None, None)
    except TypeError, e:
        if 'argument' not in str(e): # or indeed `arguments'
            raise AssertionError('Unexpected (non-arguments error) message: {}', repr(str(e)))
        return
    raise AssertionError('Expected "TypeError" to be raised (for bad number of arguments).')

def raiser(*a, **k):
    raise AssertionError('Should never be called!')
