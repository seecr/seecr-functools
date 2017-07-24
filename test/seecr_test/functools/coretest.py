from unittest import TestCase

from copy import deepcopy, copy

from seecr.functools.core import first, second, identity, some_thread, fpartial, comp, reduce, is_reduced, ensure_reduced, unreduced, reduced, completing, transduce, take, cat, map, run, filter, complement, remove, juxt, is_thruthy
from seecr.functools.string import strip, split

class CoreTest(TestCase):
    def testIdentity(self):
        self.assertRaises(TypeError, lambda: identity())
        self.assertRaises(TypeError, lambda: identity(1, 2))
        self.assertEquals(1, identity(1))
        o = object()
        self.assertTrue(o is identity(o))

    def test_is_thruthy(self):
        self.assertEquals(False, is_thruthy(0))
        self.assertEquals(False, is_thruthy(''))
        self.assertEquals(False, is_thruthy([]))
        self.assertEquals(False, is_thruthy({}))
        self.assertEquals(False, is_thruthy(None))
        self.assertEquals(False, is_thruthy(False))

        self.assertEquals(True, is_thruthy(1))
        self.assertEquals(True, is_thruthy(-1))
        self.assertEquals(True, is_thruthy('-'))
        self.assertEquals(True, is_thruthy([0]))
        self.assertEquals(True, is_thruthy({'x': 'y'}))
        self.assertEquals(True, is_thruthy(True))

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
