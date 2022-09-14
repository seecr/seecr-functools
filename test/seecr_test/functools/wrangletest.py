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

from copy import deepcopy

from seecr.functools.core import before, fpartial, append
from seecr.functools.string import strip
from seecr.functools.wrangle import fix, to_fix


class WrangleTest(TestCase):
    def testFix(self):
        x = object()
        def not_this_one():
            self.fail('Oh no!')


        def sole_function(x):
            return "should see this"

        # Last clause if uneven is non-conditionally executed if reached.
        self.assertEqual("a", fix(" a   ", lambda x: None, lambda x:None, strip))
        self.assertEqual(42, fix(" a   ", lambda x: True, lambda x: 42, strip))
        self.assertEqual("should see this", fix("a", sole_function))

        # Any value can be `fixed'
        self.assertEqual(None, fix(None))
        self.assertEqual('zz', fix('zz'))
        self.assertEqual({'a': ['x']}, fix({'a': ['x']}))
        self.assertEqual(x, fix(x))

        # Default input == output
        self.assertTrue(x is fix(x))

        # No clauses
        self.assertEqual(x, fix(x))

        # Single (Truthy - test) clause
        self.assertEqual(42, fix(x, True, 42))
        self.assertEqual(42, fix(x, object(), 42))
        self.assertEqual(42, fix(x, ['x'], 42))
        self.assertEqual((42, x), fix(x, lambda a: True, lambda a: (42, a)))
        self.assertEqual((42, x), fix(x, lambda a: object(), lambda a: (42, a)))
        self.assertEqual(x, fix(x, lambda a: a == x, lambda a: a))

        # Single (Falsy - test) clause
        self.assertEqual(x, fix(x, None, 42))
        self.assertEqual(x, fix(x, lambda n: None, lambda: 42))
        self.assertEqual(x, fix(x, False, 42))
        self.assertEqual(x, fix(x, lambda n: False, lambda: 42))
        self.assertEqual('x', fix('x', '', 42))
        self.assertEqual('x', fix('x', lambda n: '', lambda: 42))
        self.assertEqual('x', fix('x', '', lambda n: not_this_one()))
        self.assertEqual('x', fix('x', lambda n: '', lambda n: not_this_one()))

        # 2 clauses (first true -> 2nd not evaluated)
        self.assertEqual(False, fix(x,
                                     True, False,
                                     True, not_this_one))
        self.assertEqual(False, fix(x,
                                     lambda a: True, lambda a: False,
                                     lambda a: True, not_this_one))
        self.assertEqual(False, fix(x,
                                     True, False,
                                     None, not_this_one))

        # 2 clauses (both false -> input returned)
        self.assertEqual(x, fix(x,
                                 False, False,
                                 '', not_this_one))
        self.assertEqual(x, fix(x,
                                 lambda a: '', lambda a: not_this_one,
                                 lambda a: 0, None))
        self.assertEqual(x, fix(x,
                                 None, False,
                                 None, 'x'))

        # n-clauses (evaluation stops at first thuthy testresult' fn invokation)
        o_in = ['in']
        initial_in = deepcopy(o_in)

        log = []
        def logging(who):
            def _logging(_in):
                append(log, (who, _in))

            return _logging

        def val(result):
            def _val(_in):
                return result
            return _val

        t1_no = before(val(None), logging('t1_no'))
        t2_no = before(val(False), logging('t2_no'))
        t3_yes = before(val(True), logging('t3_yes'))
        t4_yes = before(val('x'), logging('t4_yes'))
        fn1 = before(val(1), logging('fn1'))
        fn2 = before(val(2), logging('fn2'))
        fn3 = before(val(3), logging('fn3'))
        fn4 = before(val(4), logging('fn4'))
        self.assertEqual(3, fix(initial_in,
                                 t1_no, fn1,
                                 t2_no, fn2,
                                 t3_yes, fn3,
                                 t4_yes, fn4))
        self.assertEqual([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)

    def testTo_fix(self):
        # Test clauses fpartial wrapping, functionality tested in testFix
        o_in = ['in']
        initial_in = deepcopy(o_in)

        log = []
        def logging(who):
            def _logging(_in):
                append(log, (who, _in))

            return _logging

        def val(result):
            def _val(_in):
                return result
            return _val

        t1_no = before(val(None), logging('t1_no'))
        t2_no = before(val(False), logging('t2_no'))
        t3_yes = before(val(True), logging('t3_yes'))
        t4_yes = before(val('x'), logging('t4_yes'))
        fn1 = before(val(1), logging('fn1'))
        fn2 = before(val(2), logging('fn2'))
        fn3 = before(val(3), logging('fn3'))
        fn4 = before(val(4), logging('fn4'))
        f = to_fix(t1_no, fn1,
                   t2_no, fn2,
                   t3_yes, fn3,
                   t4_yes, fn4)

        # Twice - 1/2
        self.assertEqual(3, f(initial_in))
        self.assertEqual([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)
        self.assertEqual(o_in, initial_in)

        # Twice - 2/2
        del log[:]
        self.assertEqual(3, f(initial_in))
        self.assertEqual([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)
        self.assertEqual(o_in, initial_in)
