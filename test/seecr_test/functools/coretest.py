from unittest import TestCase

from seecr.functools.core import first, second, identity, some_thread, fpartial, comp, reduce, is_reduced, ensure_reduced, unreduced, reduced


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
