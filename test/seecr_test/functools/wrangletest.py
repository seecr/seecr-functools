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
        self.assertEquals("a", fix(" a   ", lambda x: None, lambda x:None, strip))
        self.assertEquals(42, fix(" a   ", lambda x: True, lambda x: 42, strip))
        self.assertEquals("should see this", fix("a", sole_function))

        # Any value can be `fixed'
        self.assertEquals(None, fix(None))
        self.assertEquals('zz', fix('zz'))
        self.assertEquals({'a': ['x']}, fix({'a': ['x']}))
        self.assertEquals(x, fix(x))

        # Default input == output
        self.assertTrue(x is fix(x))

        # No clauses
        self.assertEquals(x, fix(x))

        # Single (Truthy - test) clause
        self.assertEquals(42, fix(x, True, 42))
        self.assertEquals(42, fix(x, object(), 42))
        self.assertEquals(42, fix(x, ['x'], 42))
        self.assertEquals((42, x), fix(x, lambda a: True, lambda a: (42, a)))
        self.assertEquals((42, x), fix(x, lambda a: object(), lambda a: (42, a)))
        self.assertEquals(x, fix(x, lambda a: a == x, lambda a: a))

        # Single (Falsy - test) clause
        self.assertEquals(x, fix(x, None, 42))
        self.assertEquals(x, fix(x, lambda n: None, lambda: 42))
        self.assertEquals(x, fix(x, False, 42))
        self.assertEquals(x, fix(x, lambda n: False, lambda: 42))
        self.assertEquals('x', fix('x', '', 42))
        self.assertEquals('x', fix('x', lambda n: '', lambda: 42))
        self.assertEquals('x', fix('x', '', lambda n: not_this_one()))
        self.assertEquals('x', fix('x', lambda n: '', lambda n: not_this_one()))

        # 2 clauses (first true -> 2nd not evaluated)
        self.assertEquals(False, fix(x,
                                     True, False,
                                     True, not_this_one))
        self.assertEquals(False, fix(x,
                                     lambda a: True, lambda a: False,
                                     lambda a: True, not_this_one))
        self.assertEquals(False, fix(x,
                                     True, False,
                                     None, not_this_one))

        # 2 clauses (both false -> input returned)
        self.assertEquals(x, fix(x,
                                 False, False,
                                 '', not_this_one))
        self.assertEquals(x, fix(x,
                                 lambda a: '', lambda a: not_this_one,
                                 lambda a: 0, None))
        self.assertEquals(x, fix(x,
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
        self.assertEquals(3, fix(initial_in,
                                 t1_no, fn1,
                                 t2_no, fn2,
                                 t3_yes, fn3,
                                 t4_yes, fn4))
        self.assertEquals([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)

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
        self.assertEquals(3, f(initial_in))
        self.assertEquals([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)
        self.assertEquals(o_in, initial_in)

        # Twice - 2/2
        del log[:]
        self.assertEquals(3, f(initial_in))
        self.assertEquals([('t1_no', o_in), ('t2_no', o_in), ('t3_yes', o_in), ('fn3', o_in)], log)
        self.assertEquals(o_in, initial_in)
