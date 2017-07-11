from unittest import TestCase

from seecr.functools.core import first, second, identity, some_thread, fpartial, comp


class CoreTest(TestCase):
    def testIdentity(self):
        self.assertRaises(TypeError, lambda: identity())
        self.assertRaises(TypeError, lambda: identity(1, 2))
        self.assertEquals(1, identity(1))
        o = object()
        self.assertTrue(o is identity(o))

    def testFirst(self):
        self.assertEquals(None, first(None))
        self.assertEquals(None, first([]))
        g = (x for x in [])
        self.assertEquals(None, first(g))
        self.assertEquals("a", first(["a"]))
        self.assertEquals("a", first(["a", "b"]))
        g = (x for x in [42])
        self.assertEquals(42, first(g))

    def testSecond(self):
        self.assertEquals(None, second(None))
        self.assertEquals(None, second([]))
        self.assertEquals(None, second([1]))
        self.assertEquals(2, second([1, 2]))
        self.assertEquals(2, second([1, 2, 3]))

    def testSome_thread(self):
        def make_none(x):
            return None
        def add_five(x):
            return x+5
        def add_three(x):
            return x+3

        self.assertEqual(13, some_thread(5, add_five, add_three))
        self.assertEqual(None, some_thread(5, add_three, make_none, add_five))

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
