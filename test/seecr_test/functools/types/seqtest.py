from __future__ import absolute_import

from unittest import TestCase

import __builtin__

from seecr.functools.core import cons, first, rest, next, seq, run
from seecr.functools.types import ISeq, _EmptyPersistentSinglyLinkedList, _Seq, seq_first

l = list
e = _EmptyPersistentSinglyLinkedList


class SeqTest(TestCase):
    def test_first(self):
        self.assertEquals(None, first(_Seq(None, None)))
        self.assertEquals(1, first(_Seq(1, None)))
        self.assertEquals({'x'}, first(_Seq({'x'}, None)))

        a = _Seq("a", None)
        self.assertEquals("a", seq_first(a))
        self.assertEquals("a", a.first())

        b = _Seq(None, _Seq('b', None))
        self.assertEquals(None, seq_first(b))
        self.assertEquals(None, b.first())

    def test_seq(self):
        a = _Seq("a", None)
        self.assertEquals(a, seq(a))
        self.assertTrue(a is a.seq() is seq(a))

        b = _Seq(None, _Seq(2, None))
        self.assertEquals(b, seq(b))
        self.assertTrue(b is b.seq() is seq(b))

        c = _Seq(None, None)
        self.assertEquals(c, seq(c))
        self.assertEquals(_Seq, type(seq(c)))
        self.assertTrue(c is c.seq() is seq(c))

    def test_next(self):
        a = _Seq("a", None)
        self.assertEquals(None, next(a))
        self.assertEquals(None, a.next_())

        b_rest_seq = _Seq('b', None)
        b = _Seq(None, b_rest_seq)
        self.assertEquals(b_rest_seq, next(b))
        self.assertEquals(['b'], l(next(b)))
        self.assertEquals(b_rest_seq, b.next_())
        self.assertEquals(['b'], l(b.next_()))

        ab = _Seq('a', b_rest_seq)
        self.assertEquals(b_rest_seq, next(ab))
        self.assertEquals(['b'], l(ab.next_()))

        bc_seq = _Seq('b', _Seq('c', _EmptyPersistentSinglyLinkedList)) # None <-> _EmptyPersistentSinglyLinkedList (basically any empty-seq) can be used interchangably here.
        abc = _Seq('a', bc_seq)
        self.assertEquals(bc_seq, next(abc))
        self.assertEquals(['b', 'c'], l(next(abc)))
        self.assertEquals(['b', 'c'], l(abc.next_()))
        self.assertEquals(['c'], l(next(next(abc))))
        self.assertEquals(['c'], l(abc.next_().next_()))
        self.assertEquals(None, next(next(next(abc))))
        self.assertEquals(None, abc.next_().next_().next_())
        self.assertEquals(None, next(next(next(next(abc)))))
        self.assertRaises(AttributeError, lambda: abc.next_().next_().next_().next_())

    def test_rest(self):
        empty_rest = _Seq('whatever', None)
        self.assertTrue(_EmptyPersistentSinglyLinkedList is rest(empty_rest) is empty_rest.rest())
        self.assertEquals([], l(rest(empty_rest)))
        self.assertEquals([], l(empty_rest.rest()))

        nonempty_rest_with_empty_psll = _Seq('whatever', _EmptyPersistentSinglyLinkedList)
        self.assertTrue(_EmptyPersistentSinglyLinkedList is rest(nonempty_rest_with_empty_psll) is nonempty_rest_with_empty_psll.rest())
        self.assertEquals([], l(rest(nonempty_rest_with_empty_psll)))

        nonempty_rest_none_value = _Seq('whatever', _Seq(None, None))
        self.assertTrue(_Seq, type(rest(nonempty_rest_none_value)))
        self.assertEquals([None], l(rest(nonempty_rest_none_value)))
        self.assertEquals([None], l(nonempty_rest_none_value.rest()))

        nonempty_rest_a_value = _Seq('whatever', _Seq('a', None))
        self.assertTrue(_Seq, type(rest(nonempty_rest_a_value)))
        self.assertEquals(['a'], l(rest(nonempty_rest_a_value)))
        self.assertEquals(['a'], l(nonempty_rest_a_value.rest()))

    def test_ISeq(self):
        self.assertTrue(isinstance(_Seq('whatever', None), ISeq))

        # works with cons -> so must be an ISeq instance.
        self.assertEquals([1, 2], l(cons(1, _Seq(2, None))))
        self.assertEquals([1, 2], l(cons(1, _Seq(2, _EmptyPersistentSinglyLinkedList))))

    def test_cons_typechecks(self):
        # non "ISeq-or-None" value errs in cons, **not** when calling _Seq(...) directly!
        obj = object()
        nested = _Seq('nested', None)
        two = _Seq(2, None)
        pairs = [               # ((val, ISeq-or-None), cons-error-expected-boolean, result-iff-no-expected-error)
            # 1-val
            ((None, None), False, [None]),
            (('a', None), False, ['a']),
            ((obj, None), False, [obj]),
            ((nested, None), False, [nested]),

            # 2..n-val
            ((None, two), False, [None, 2]),
            (('a', two), False, ['a', 2]),
            ((obj, two), False, [obj, 2]),
            ((nested, two), False, [nested, 2]),
            ((nested, _Seq(nested, two)), False, [nested, nested, 2]),

            # bad-val
            ((None, obj), True, None),
            (('a', False), True, None),
            (('a', ()), True, None),
            (('a', set()), True, None),
            ((obj, 0), True, None),
            ((nested, []), True, None),
        ]
        def assert_pair(t):
            args, cons_err_or_none, expected = t
            # cons
            if cons_err_or_none:
                try:
                    cons(*args)
                    self.fail()
                except ValueError:
                    pass

            else:
                self.assertEquals(expected, l(cons(*args)))

            # _Seq
            if not cons_err_or_none:  # Undefined behaviour for invalid _Seq "more" / rest; so don't try to test.
                self.assertEquals(expected, l(_Seq(*args)))

        run(assert_pair, pairs)

    def test_iter(self):
        self.assertEquals([None], l(_Seq(None, None)))
        self.assertEquals([1], l(_Seq(1, None)))
        self.assertEquals([1, 2], l(_Seq(1, _Seq(2, None))))
        _123 = cons(1, cons(2, cons(3, None)))
        _123_iter = iter(_123)
        self.assertEquals([1, 2, 3], l(_123_iter))
        self.assertEquals([], l(_123_iter)) # stateful cursor - can only iterate once.
        self.assertEquals([], l(_123_iter)) # lazy-seq can be (re-)iterated

    def test_smells_immutable(self):
        # object.__setattr__(...) still works, but if you ignore common-sense ...
        s = _Seq(1, None)
        self.assertRaises(TypeError, lambda: setattr(s, 'somename', 'a-value'))
        try:
            del s.somename
        except TypeError:
            pass
        else: self.fail()
