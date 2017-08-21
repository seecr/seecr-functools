# TODO:
#  - lazy_from_iter()  # and/or generator --> user needs to be careful that its not a **composed-generator**, same as with other iterator-consuming-code.
from __future__ import absolute_import

from sys import exc_info
from abc import ABCMeta

import __builtin__
import functools as _python_functools
import collections as _python_collections

_functools_partial = _python_functools.partial

# Sentinels
_not_found = type('NOT_FOUND', (object,), {})()


# ABC markers
class ISeq(object):
    """
    Abstract base-class `marker' signaling `seq'-methods are implemented:

    FIXME: Describe which methods?
    """
    __metaclass__ = ABCMeta

# Overwritten builtins & associated
def seq(coll):
    """
    Returns a seq on the collection. If the collection is
    empty, returns None.  (seq None) returns None.

    seq also works on strings, (python) lists, iterables or dictionaries (iff they implement iteritems).
    """
    if coll is not None:
        return coll.seq()

def next(coll):
    if coll is not None:
        return coll.next_()

def seq_first(coll):
    if coll is not None:
        return coll.first()

def rest(coll):
    if coll is None:
        return _EmptyPersistentSinglyLinkedList
    return coll.rest()

# Class helpers
def _no_setattr(self, name, value):
    raise TypeError("'{}' object doesn't support item assignment".format(self.__class__.__name__))

def _no_delattr(self, name):
    raise TypeError("'{}' object doesn't support item deletion".format(self.__class__.__name__))


# # ISeq
#
# Object first();
#
# ISeq next();
#
# ISeq more();
#
# ISeq cons(Object o);
#
# # IPersistentCollection
#
# int count();
#
# IPersistentCollection cons(Object o);
#
# IPersistentCollection empty();
#
# boolean equiv(Object o);
#
# # Seqable
#
# ISeq seq();
#
# # IPending
#
# boolean isRealized();
#
# # Sequential
#
# ## marker only!
#
# # IHashEq
#
# int hasheq();

class __EmptyPersistentSinglyLinkedList(object):
    __slots__ = ()
    __setattr__ = _no_setattr
    __delattr__ = _no_delattr

    def first(self):
        return None

    def seq(self):
        return None

    def next_(self):
        return None

    def next(self):
        # The <iterator>.next() variant
        raise StopIteration()

    def rest(self):
        return self

    def __iter__(self):
        return self

_EmptyPersistentSinglyLinkedList = __EmptyPersistentSinglyLinkedList() # Singleton

class _Seq(object):
    __slots__ = ('_first', '_more')
    __setattr__ = _no_setattr
    __delattr__ = _no_delattr

    def __init__(self, _first, _more):
        _obj_setattr(self, '_first', _first)
        _obj_setattr(self, '_more', _more)

    def first(self):
        return self._first

    def seq(self):
        return self

    def next_(self):
        return seq(self._more) # FIXME: next -> rest-ish

    def rest(self):
        m = self._more
        if m is None:
            return _EmptyPersistentSinglyLinkedList
        return m

    def __iter__(self):
        def _seq_iterable():
            s = self
            while s:
                yield s.first()
                s = seq(s.rest())
        return _seq_iterable()


class _LazySeq(object):
    __slots__ = ('_fn', '_v', '_seq')
    __setattr__ = _no_setattr
    __delattr__ = _no_delattr

    def __init__(self, fn):
        _obj_setattr(self, '_fn', fn)
        _obj_setattr(self, '_seq',  _not_found)

    def first(self):
        return seq_first(self.seq())

    def _seq_step(self):
        fn = self._fn
        if fn is None:
            if self._seq is _not_found:
                return (False, self._v)
            else:
                return (True, self._seq)

        try:
            v = fn()
        except BaseException:
            _c, _v, _t = exc_info()
            if getattr(fn, '__not_raised__', True):
                _r = _functools_partial(_reraise, _c, _v, _t.tb_next)  # shave one tb-layer off, since re-raising goes through here anyway.
                _r.__not_raised__ = False
                _obj_setattr(self, '_fn', _r)

            raise _c, _v, _t
        else:
            _obj_setattr(self, '_fn', None)
            _obj_setattr(self, '_v', v)

        return (False, v)

    def seq(self):
        realized, v = self._seq_step()
        if realized is True:
            return v

        while isinstance(v, _LazySeq): # FIXME: |
            _, v = v._seq_step()       # FIXME: \--> THINK: can realized value of intermediate be used, or not?

        v = seq(v)
        _obj_setattr(self, '_seq', v)
        return v

    def next_(self):
        return next(self.seq())

    def rest(self):
        return rest(self.seq())

    def is_realized(self):
        return self._fn is None

    def __iter__(self):
        def _ls_iterable():
            s = self.seq()
            while s:
                yield s.first()
                s = seq(s.rest())
        return _ls_iterable()


_obj_setattr = object.__setattr__

def _reraise(_c, _v, _t):
    raise _c, _v, _t


__builtin__.map(ISeq.register,
                [__EmptyPersistentSinglyLinkedList, _Seq, _LazySeq])
__builtin__.map(_python_collections.Iterable.register,
                [__EmptyPersistentSinglyLinkedList, _Seq, _LazySeq])
