from __future__ import absolute_import

from unittest import TestCase

import __builtin__

from seecr.functools.core import cons, first, rest, next, seq
from seecr.functools.types import ISeq, _EmptyPersistentSinglyLinkedList, _LazySeq, _Seq, seq_first

l = list
e = _EmptyPersistentSinglyLinkedList


class EmptyPersistentSinglyLinkedListTest(TestCase):
    def test_first(self):
        self.assertEquals(None, first(e))
        self.assertEquals(None, seq_first(e))
        self.assertEquals(None, e.first())

    def test_seq(self):
        self.assertEquals(None, seq(e))
        self.assertEquals(None, e.seq())

    def test_next(self):
        self.assertEquals(None, next(e))
        self.assertEquals(None, e.next_())

    def test_rest(self):
        self.assertTrue(_EmptyPersistentSinglyLinkedList is rest(_EmptyPersistentSinglyLinkedList))
        self.assertTrue(_EmptyPersistentSinglyLinkedList is _EmptyPersistentSinglyLinkedList.rest())

    def test_ISeq(self):
        self.assertTrue(isinstance(_EmptyPersistentSinglyLinkedList, ISeq))

        # works with cons -> so must be an ISeq instance.
        self.assertEquals([1], l(cons(1, _EmptyPersistentSinglyLinkedList)))

    def test_iter(self):
        self.assertEquals([], l(e))
        self.assertEquals([], l(e)) # Immutable type ...
        self.assertEquals(iter(e), iter(e)) # ... and iterator, since a stateful-cursor always being empty == stateless empty.

    def test_smells_immutable(self):
        # object.__setattr__(...) still works, but if you ignore common-sense ...
        self.assertRaises(TypeError, lambda: setattr(e, 'somename', 'a-value'))
        try:
            del e.somename
        except TypeError:
            pass
        else: self.fail()
