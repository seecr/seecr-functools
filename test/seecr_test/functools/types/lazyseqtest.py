from __future__ import absolute_import

from unittest import TestCase

import __builtin__

from itertools import permutations
from sys import exc_info

from seecr.functools.core import lazy_seq, cons, first, rest, next, seq, run, is_realized
from seecr.functools.types import ISeq, _EmptyPersistentSinglyLinkedList, _LazySeq, _Seq


class LazySeqTest(TestCase):
    def test_empty_via_None(self):
        thunk = lambda: None

        def prep():
            s = lazy_seq(thunk)
            self.assertEquals(None, s._seq)
            self.assertEquals(thunk, s._fn)
            self.assertEquals(False, is_realized(s))
            return s

        def post(s):
            self.assertEquals(None, s._seq)
            self.assertEquals(None, s._fn)
            self.assertEquals(True, is_realized(s))

        def test_one(tf):
            s = prep()
            tf(s)
            post(s)

        def test_all(tfs):
            s = prep()
            run(lambda tf: tf(s), tfs)
            post(s)

        t_seq_m = lambda s: self.assertEquals(None, s.seq())
        t_seq_f = lambda s: self.assertEquals(None, seq(s))
        t_first_m = lambda s: self.assertEquals(None, s.first())
        t_first_f = lambda s: self.assertEquals(None, first(s))
        t_next_m = lambda s: self.assertEquals(None, s.next_())
        t_next_f = lambda s: self.assertEquals(None, next(s))
        t_rest_m = lambda s: self.assertEquals(_EmptyPersistentSinglyLinkedList, s.rest())
        t_rest_f = lambda s: self.assertEquals(_EmptyPersistentSinglyLinkedList, rest(s))

        m_test_fns = [t_seq_m, t_first_m, t_next_m, t_rest_m]
        all_test_fns = [t_seq_m, t_seq_f, t_first_m, t_first_f, t_next_m, t_next_f, t_rest_m, t_rest_f]

        run(test_one, all_test_fns)
        run(test_all, permutations(m_test_fns))

    def test_empty_via_emptypll(self):
        s = lazy_seq(lambda: _EmptyPersistentSinglyLinkedList)
        self.assertEquals(False, is_realized(s))
        self.assertEquals(None, first(s))
        self.assertEquals(True, is_realized(s))

        self.assertEquals(None, seq(s))
        self.assertEquals(None, next(s))
        self.assertTrue(_EmptyPersistentSinglyLinkedList is rest(s))

    def test_nested_empy_lazy_seq(self):
        s = lazy_seq(lambda: lazy_seq(lambda: None))
        self.assertEquals(None, seq(s))

        s = lazy_seq(lambda: lazy_seq(lambda: _EmptyPersistentSinglyLinkedList))
        self.assertEquals(None, seq(s))

    def test_one_val(self):
        def test(s, rest_val=_EmptyPersistentSinglyLinkedList):
            for _ in range(2):
                self.assertEquals([42],  list(seq(s)))
                self.assertEquals(42, first(s))
                self.assertEquals(rest_val, rest(s))
                self.assertEquals(None, first(rest(s)))
                self.assertEquals(None, next(s))

        test(lazy_seq(lambda: cons(42, None)))
        test(lazy_seq(lambda: cons(42, _EmptyPersistentSinglyLinkedList)))
        _rst = lazy_seq(lambda: None)
        test(lazy_seq(lambda: cons(42, _rst)),
             _rst)
        _rst = lazy_seq(lambda: _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, _rst)),
             _rst)

    def test_two_val(self):
        def test(s, rest_1_type, rest_2_val):
            for _ in range(2):
                self.assertEquals([42, 43],  list(seq(s)))
                self.assertEquals(42, first(s))
                self.assertEquals(rest_1_type, type(rest(s)))
                self.assertEquals(rest_2_val, rest(rest(s)))
                self.assertEquals(43, first(rest(s)))
                self.assertEquals(None, first(rest(rest(s))))
                self.assertEquals(43, next(s))
                self.assertEquals(None, next(rest(s)))

        test(lazy_seq(lambda: cons(42, cons(43, None))),
             _Seq,
             _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, lazy_seq(lambda: cons(43, None)))),
             _LazySeq,
             _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, cons(43, _EmptyPersistentSinglyLinkedList))),
             _Seq,
             _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, lazy_seq(lambda: cons(43, _EmptyPersistentSinglyLinkedList)))),
             _LazySeq,
             _EmptyPersistentSinglyLinkedList)
        _rst = lazy_seq(lambda: None)
        test(lazy_seq(lambda: cons(42, cons(43, _rst))),
             _Seq,
             _rst)
        _rst = lazy_seq(lambda: _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, cons(43, _rst))),
             _Seq,
             _rst)
        test(lazy_seq(lambda: cons(42, lazy_seq(lambda: cons(43, _rst)))),
             _LazySeq,
             _rst)
        _rst = lazy_seq(lambda: _EmptyPersistentSinglyLinkedList)
        test(lazy_seq(lambda: cons(42, lazy_seq(lambda: cons(43, _rst)))),
             _LazySeq,
             _rst)

    def test_fully_lazy_evaluation(self):
        _realized = []
        def realized():
            vs = _realized[:]
            del _realized[:]
            return vs

        def lz_cns(v, rst):
            return lazy_seq(lambda: _realized.append(v) or cons(v, rst))

        def make_s():
            return lz_cns(1, lz_cns(2, lz_cns(3, lazy_seq(lambda: _realized.append('done')))))

        s = make_s()
        # 1st-value not created before it is required
        self.assertEquals([], realized())
        self.assertEquals(1, first(s))
        s2 = rest(s)
        self.assertEquals([1], realized())

        # re-reading an already realized part of a persistent-lazy-seq has no effects anymore.
        self.assertEquals(1, first(s))
        self.assertEquals([], realized())

        # 2nd value  "   "        "   "   "    "
        self.assertEquals(2, first(s2))
        self.assertEquals([2], realized())
        self.assertEquals(2, next(s))
        s3 = rest(s2)

        # Same goes for __iter__ -> iterable
        it = iter(s2)
        self.assertEquals([], realized())
        self.assertEquals(2, __builtin__.next(it))
        self.assertEquals([], realized())
        self.assertEquals(3, __builtin__.next(it))
        self.assertEquals([3], realized())
        self.assertEquals(3, first(s3))
        self.assertEquals(_LazySeq, type(rest(s3)))
        self.assertEquals([], realized())

        # last "empty" part is an empty-lazy-seq.
        self.assertEquals(None, next(s3))
        self.assertEquals(['done'], realized())

        # seq - 1st
        s = make_s()
        self.assertEquals([], realized())
        s_seq = seq(s)
        self.assertEquals([1], realized())
        self.assertTrue(1 == first(s_seq) == first(s))
        self.assertEquals([], realized())

        # seq - 3rd
        s_seq3 = seq(rest(rest(s)))
        self.assertEquals([2, 3], realized())
        self.assertEquals(3, first(s_seq3))
        self.assertEquals([], realized())

        # seq - last
        s_seq3 = seq(rest(rest(rest(s))))
        self.assertEquals(['done'], realized())
        self.assertEquals(None, first(s_seq3))
        self.assertEquals(None, next(s_seq3))
        self.assertEquals(_EmptyPersistentSinglyLinkedList, rest(s_seq3))
        self.assertEquals(None, seq(s_seq3))
        self.assertEquals([], realized())

    def test_recursion(self):
        _called = []
        def called():
            c = _called[:]
            del _called[:]
            return c

        def count_to(n):
            def step(s):
                def _():
                    _called.append(s)
                    if s > n:
                        return None
                    return cons(s, step(s + 1))
                return lazy_seq(_)
            return step(1)

        c = count_to(1)
        self.assertEquals([], called())
        self.assertEquals(1, first(c))
        self.assertEquals([1], called())
        self.assertEquals([1], list(c))
        self.assertEquals([2], called())
        self.assertEquals([[1], 1, None, None, None], [list(c), first(c), next(c), first(rest(c)), next(rest(c))])
        self.assertEquals([], called())

        self.assertEquals([1, 2, 3], list(count_to(3)))
        self.assertEquals([1, 2, 3, 4], called())

        self.assertEquals(1, first(count_to(3)))
        self.assertEquals([1], called())
        self.assertEquals(_LazySeq, type(rest(count_to(3))))
        self.assertEquals([1], called())
        self.assertEquals(2, next(count_to(3)))
        self.assertEquals([1, 2], called())
        self.assertEquals(_Seq, type(seq(count_to(3))))
        self.assertEquals([1], called())

    def test_mutual_recursion(self):
        # For fun!
        def ping():
            return lazy_seq(lambda: cons('ping', pong()))
        def pong():
            return lazy_seq(lambda: cons('pong', ping()))

        r = []
        s = ping()
        for _ in range(6):
            r.append(first(s))
            s = rest(s)

        self.assertEquals(['ping', 'pong', 'ping', 'pong', 'ping', 'pong'], r)

    def test_recursive_fib(self):
        # Sorry, some more fun.

        # Recursive fn
        def _fib1_seq(a, b):
            def _():
                return cons(a, _fib1_seq(b, a + b))
            return lazy_seq(_)
        def fib1():
            return _fib1_seq(0, 1)

        s = fib1()
        self.assertEquals(0, first(s))
        self.assertEquals(1, first(rest(s)))
        self.assertEquals(1, first(rest(rest(s))))
        res = []
        ss = s
        for _ in range(10):
            res.append(first(ss))
            ss = rest(ss)
        self.assertEquals([0, 1, 1, 2, 3, 5, 8, 13, 21, 34], res)

        # Recursive via seq
        def lazy_cat(*a):       # FIXME: rename to `concat' & test?
            def _():
                _1 = first(a)
                if seq(_1):
                    return cons(first(_1), lazy_cat(rest(_1), *a[1:]))

                remaining = list(a[1:])
                while remaining:
                    _n, remaining = first(remaining), remaining[1:]
                    return lazy_cat(_n, *remaining)

            return lazy_seq(_)

        def mp(f, c1, c2):      # FIXME: fix in map, remove this fn here.
            def _():
                v1, v2 = seq(c1), seq(c2)
                if v1 and v2:
                    return cons(f(first(v1), first(v2)), mp(f, rest(v1), rest(v2)))
            return lazy_seq(_)

        global _fib2
        def r():
            global _fib2
            return mp(lambda a,b: (a or 0) + (b or 0), rest(_fib2), _fib2)
        _fib2 = lazy_cat(cons(0, cons(1, None)), lazy_seq(r))

        ss = _fib2
        res = []
        for _ in range(10):
            res.append(first(ss))
            ss = rest(ss)

        self.assertEquals([0, 1, 1, 2, 3, 5, 8, 13, 21, 34], res)

    def test_error_from_fn_saved_and_reraised(self):
        class FancyException(Exception):
            pass

        _raised = []
        def in_between():
            if not _raised:
                _raised.append(True)
                raise FancyException('Very Fancy')

        def raiser():
            return in_between()

        s_one = lazy_seq(raiser)
        s_two = lazy_seq(lambda: cons(1, lazy_seq(raiser)))

        try:
            seq(s_one)
            self.fail('should not happen')
        except FancyException, e:
            c, v, t = exc_info()
            self.assertEquals(FancyException, c)
            self.assertEquals(v, e)
            self.assertEquals('Very Fancy', str(e))
            names = []
            while t:
                names.append(t.tb_frame.f_code.co_name)
                t = t.tb_next
            self.assertEquals(['test_error_from_fn_saved_and_reraised', 'seq', 'seq', 'raiser', 'in_between'], names)

        # FIXME: test _raised & not re-raising iff called again - but is so iff lazy-seq'ed.
        self.fail()

_fib2 = None                    # global used in `test_recursive_fib'

# TODO:
# 1.5. one raised error -> keeps getting reraised!
# 2. Recusion/multiple-lazy-seqs does not use:
#    - stack space
# 2.5. chained non-value lazy-seq's do not use > 1x stack-space when realizing the next value (see sval / seq impl of Clojure LazySeq)
# 2.7. See `concat-bomb' and solution iff relevant / handy to process into Py.
# 2.8. `concat-bomb' is basically a meaning/intention <-> implementation mismatch (in Clojure only?) ==> should (be possible) to have "simple" solution given a logic-lang.
#
#        (Think...)
#
# 3. When not "holding on to your head" - values of:
#     - cons
#     - lazy_seq
#    Get GC'ed!
#
#    A.k.a.: infinite sequences are ok!
#
# 4. add iter/non-effecting-gen->lazy-seq fn & tests
# 5. add effecting-gen->lazy-seq(almostness - effects wrapped & returned only once!).
