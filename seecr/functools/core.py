# -*- coding: utf-8 -*-
from __future__ import absolute_import

import __builtin__

from itertools import izip as _itertools_izip

from .types import _not_found, ISeq, _Seq, _LazySeq, seq, rest, next

#
# re-defined builtins
_builtin_next = __builtin__.next

#
# collection & seq basics
def cons(x, seq_):               # FIXME: Test Me
    """
    Returns a new seq where x is the first element and seq is the rest; seq must be in ISeq ABC-registered `instance' or implement __iter__ (≈ iterable or generator) or iteritems (dict-like).
    """
    if (seq_ is None) or isinstance(seq_, ISeq):
        return _Seq(x, seq_)
    raise ValueError('seq must be an ISeq (ABC-registered class-instance) or None.')

    # if (seq_ is None) or isinstance(seq_, ISeq):
    #     return _Seq(x, seq_)
    # raise ValueError('seq must be an ISeq (ABC-registered class-instance) or None.')

def lazy_seq(thunk):
    if not callable(thunk):
        raise ValueError('thunk must be a callable 0-arity fn') # FIXME: Test Me
    return _LazySeq(thunk)

def first(coll):                # FIXME: test for seq-stuff
    if coll:
        if isinstance(coll, ISeq):
            return coll.first()
        else:
            for v in coll:
                return v

def second(iterable):           # FIXME: fix for seq's
    if iterable:
        iterable = iter(iterable)
        _builtin_next(iterable, None)
        return _builtin_next(iterable, None)

def is_realized(s):             # FIXME: Test Me
    return s.is_realized()

# TODO: add & test:  rest, next, seq

# TODO: nth, before, after, assoc / assoc_in, get / get_in

#
# reduced & helper-fns

class reduced(object):
    """Sentinel wrapper from which terminal value can be retrieved. If received
    by transducers.reduce, will signal early termination."""
    def __init__(self, val):
        self.val = val


def is_reduced(x):
    return isinstance(x, reduced)

def ensure_reduced(x):
    return x if is_reduced(x) else reduced(x)

def unreduced(x):
    return x.val if is_reduced(x) else x

def preserving_reduced(rf):
    def _preserving_reduced(acc, i):
        ret = rf(acc, i)
        return reduced(ret) if is_reduced(ret) else ret # Purposefully double-wrap a value in reduced.
    return _preserving_reduced


def cat(rf):
    """
    A transducer which concatenates the contents of each input, which must be a collection, into the reduction.
    """
    rrf = preserving_reduced(rf)
    def _cat_step(*a):
        if len(a) == 0:
            return rf()
        elif len(a) == 1:
            result, = a
            return rf(result)
        elif len(a) == 2:
            result, input_ = a
            return reduce(rrf, result, input_)
        else:
            raise TypeError("_cat_step takes either 0, 1 or 2 arguments ({} given)".format(len(a)))
    return _cat_step

def reduce(*a):
    """
    reduce(f, coll)
    reduce(f, val, coll)

    For loop impl of reduce in Python that honors sentinal wrapper Reduced and
    uses it to signal early termination.

    f should be a function of 2 arguments. If val is not supplied,
    returns the result of applying f to the first 2 items in coll, then
    applying f to that result and the 3rd item, etc. If coll contains no
    items, f must accept no arguments as well, and reduce returns the
    result of calling f with no arguments.  If coll has only 1 item, it
    is returned and f is not called.  If val is supplied, returns the
    result of applying f to val and the first item in coll, then
    applying f to that result and the 2nd item, etc. If coll contains no
    items, returns val and f is not called.
    """
    if len(a) == 2:
        f, coll = a[0], iter(a[1])  # Only keep a reference to the iterator, so
        del a                       # processed items can be GC'ed iff relevant.
        _1, _2 = _builtin_next(coll, _not_found), _builtin_next(coll, _not_found)
        if _1 is _not_found:
            return f()
        elif _2 is _not_found:
            return _1

        accum_value = f(_1, _2)
    elif len(a) == 3:
        f, val, coll = a[0], a[1], iter(a[2])  # Only keep a reference to the iterator, so
        del a                                  # processed items can be GC'ed iff relevant.
        accum_value = val
    else:
        raise TypeError("reduce takes either 2 or 3 arguments ({} given)".format(len(a)))

    for x in coll:
        accum_value = f(accum_value, x)
        if is_reduced(accum_value):
            return accum_value.val
    return accum_value

def map(f, *colls):
    """
    map(f)
    map(f, coll)
    map(f, coll, *colls)

    Returns a lazy sequence consisting of the result of applying f to
    the set of first items of each coll, followed by applying f to the
    set of second items in each coll, until any one of the colls is
    exhausted.  Any remaining items in other colls are ignored. Function
    f should accept number-of-colls arguments. Returns a transducer when
    no collection is provided.
    """
    if len(colls) == 0:
        def _map_xf(rf):
            def _map_step(*a):
                if len(a) == 0:
                    return rf()
                elif len(a) == 1:
                    result, = a
                    return rf(result)
                elif len(a) == 2:
                    result, input_ = a
                    return rf(result, f(input_))
                else:               # > 2 - not a transducer-arity, so needs a wrapper to transform (result, input) to (result, input_1, ..., input_n).
                    result, inputs = a[0], a[1:]
                    return rf(result, f(*inputs))
            return _map_step
        return _map_xf
    elif len(colls) == 1:
        coll = iter(colls[0])
        del colls
        def _map():
            for x in coll:
                yield f(x)
        return _map()
    else:
        _coll_items = _itertools_izip(*map(iter, colls))
        del colls
        def _map():
            for _t in _coll_items:
                yield f(*_t)
        return _map()


def filter(pred):
    """
    FIXME: Only transducer-arity implemented!

    Returns a lazy sequence of the items in coll for which
    pred(item) returns true. pred must be free of side-effects.
    Returns a transducer when no collection is provided.
    """
    def _filter_xf(rf):
        def _filter_step(*a):
            if len(a) == 0:
                return rf()
            elif len(a) == 1:
                result, = a
                return rf(result)
            elif len(a) == 2:
                result, input_ = a
                if pred(input_):
                    return rf(result, input_)
                return result
            else:
                raise TypeError("filter takes either 0, 1 or 2 arguments ({} given)".format(len(a)))
        return _filter_step
    return _filter_xf

def remove(pred):
    """
    FIXME: Only transducer-arity implemented!

    Returns a lazy sequence of the items in coll for which
    pred(item) returns false. pred must be free of side-effects.
    Returns a transducer when no collection is provided.
    """
    return filter(complement(pred))

def interleave(*colls):
    _zipped_items = _itertools_izip(*colls)
    del colls
    for _colls_item in _zipped_items:
        for i in _colls_item:
            yield i

def interpose(sep):
    """
    FIXME: Only transducer-arity implemented!

    Returns a lazy seq of the elements of coll separated by sep.
    Returns a stateful transducer when no collection is provided.
    """
    def _interpose_xf(rf):
        started = [False]
        def _interpose_step(*a):
            if len(a) == 0:
                return rf()
            elif len(a) == 1:
                result, = a
                return rf(result)
            elif len(a) == 2:
                result, input_ = a
                if started[0]:
                    _sepr = rf(result, sep)
                    if is_reduced(_sepr):
                        return _sepr
                    else:
                        return rf(_sepr, input_)
                else:
                    started[0] = True
                    return rf(result, input_)
            else:
                raise TypeError("interpose takes either 0, 1 or 2 arguments ({} given)".format(len(a)))
        return _interpose_step
    return _interpose_xf

# TODO: nth, before, after, assoc / assoc_in, get / get_in

def _none_to_empty_list(coll):
    return [] if coll is None else coll

def append(*a):
    """
    append()
    append(coll)
    append(coll, *xs)

    If coll is not given or None - uses the empty-mutable-list.
    For each x in xs, calls the (side-effecting) append-method on coll; returns coll.
    """
    if len(a) == 0:
        return []
    elif len(a) == 1:
        coll = _none_to_empty_list(a[0])
    elif len(a) == 2:
        coll, x = _none_to_empty_list(a[0]), a[1]
        coll.append(x)
    else:
        coll, xs = _none_to_empty_list(a[0]), a[1:]
        run(coll.append, xs)
    return coll

def _none_to_empty_str_or_str(s):
    return "" if s is None else str(s)

def _strng_rf(acc, e):
    return _none_to_empty_str_or_str(acc) + _none_to_empty_str_or_str(e)

def strng(*a):
    """
    strng()
    strng(x)
    strng(x, *xs)

    With no args, returns the empty string. With one arg, returns
    str(x).  strng(None) returns the empty string. With more than
    one arg, returns the concatenation of the strng values of the args.
    """
    if len(a) == 0:
        return ""
    elif len(a) == 1:
        s, = a
        return _none_to_empty_str_or_str(s)
    else:
        return reduce(_strng_rf, a)

def _set_or_update_target_d(d, keypath):
    path, leaf = keypath[:-1], keypath[-1]
    target_d = d
    if path:
        for i, p in enumerate(path):
            target_d = target_d.setdefault(p, {})
            if not isinstance(target_d, dict):
                raise ValueError('At path {} value {} is not a dict.'.format(path[:i+1], repr(target_d)))

    return target_d, leaf

def assoc(d, k, v, *kvs):
    if (len(kvs) % 2) != 0:
        raise TypeError('Uneven number of kvs')

    remaining = append([k, v], *kvs)
    while remaining:
        k, v, remaining = remaining[0], remaining[1], remaining[2:]
        d[k] = v

    return d

def assoc_in(d, keypath, v):
    target_d, leaf = _set_or_update_target_d(d, keypath)
    target_d[leaf] = v
    return d

def assoc_in_when(d, keypath, v):
    "assoc-in only when v is not None"
    if v is not None:
        return assoc_in(d, keypath, v)

    return d

def update_in(d, keypath, f, *args):
    target_d, leaf = _set_or_update_target_d(d, keypath)
    target_d[leaf] = f(target_d.get(leaf), *args)
    return d

def is_thruthy(x):
    return bool(x)

#
# Higher order fns
def identity(x):
    return x

def constantly(x):
    "Returns a function that takes any number of arguments and returns x."
    def _constantly(*a, **kw):
        return x

    return _constantly

def trampoline(f, *a, **kw):
    ret = f(*a, **kw)
    while callable(ret):
        ret = ret()
    return ret

def thrush(*a):
   "Thrush operator for python!  Should be called with an initial value and 1 or more fns to make sense."
   # See: http://blog.fogus.me/2010/09/28/thrush-in-clojure-redux/
   return reduce(lambda acc, fn: fn(acc), a)

def before(f, g):
    """"
    Returns a fn calling advice-like fn g (with all args) before calling the primary fn f (also with all args).
    Result of f will be returned.
    """
    def _before(*a, **kw):
        g(*a, **kw)
        return f(*a, **kw)

    return _before

def after(f, g):
    """"
    Returns a fn calling advice-like fn g (with all args) after calling the primary fn f (also with all args).
    Result of f will be returned.
    """
    def _after(*a, **kw):
        v = f(*a, **kw)
        g(*a, **kw)
        return v

    return _after

def complement(f):
    """
    Takes a fn f and returns a fn that takes the same arguments as f,
    has the same effects, if any, and returns the opposite truth value.
    """
    def _complement(*a, **kw):
        return not f(*a, **kw)
    return _complement

def juxt(*fns):
    """
    Takes a set of functions and returns a fn that is the juxtaposition
    of those fns.  The returned fn takes a variable number of args, and
    returns a list containing the result of applying each fn to the
    args (left-to-right).
    juxt(a, b, c)(x) => [a(x), b(x), c(x)]
    """
    def _juxt(*a, **kw):
        def rf(acc, fn):
            acc.append(fn(*a, **kw))
            return acc
        return reduce(rf, [], fns)
    return _juxt

def run(proc, coll):
    "Runs the supplied procedure, for purposes of side effects, on successive items in coll. Returns None."
    reduce(lambda acc, e: proc(e), None, coll)

def some_thread(x, *fns):
    """
    When x is not None, calls the first fn with it,
    and when that result is not None, calls the next with the result, etc.
    """
    if not fns:
        return x

    if x is None:
        return

    for f in fns:
        x = f(x)
        if x is None:
            return

    return x

def fpartial(f, *a, **kw):       # similar to: https://github.com/clojurewerkz/support/blob/master/src/clojure/clojurewerkz/support/fn.clj - but *only* first-arg is allowed & required.
    def _wrap(arg):
        return f(arg, *a, **kw)
    return _wrap

def take(*a):
    """
    take(n)
    take(n, coll)

    Returns an iterable of the first n items in coll, or all items if
    there are fewer than n.  Returns a stateful transducer when
    no collection is provided.
    """
    if len(a) == 1:
        n, = a
        del a
        def _take_xf(rf):
            _nv = [n]
            def _take_step(*a):
                if len(a) == 0:
                    return rf()
                elif len(a) == 1:
                    result, = a
                    return rf(result)
                elif len(a) == 2:
                    result, input_ = a
                    _n = _nv[0]
                    _nv[0] = _nn = _n - 1
                    result = rf(result, input_) if _n > 0 else result
                    if _nn > 0:
                        return result
                    else:
                        return ensure_reduced(result)
            return _take_step
        return _take_xf
    elif len(a) == 2:
        n, coll = a[0], iter(a[1])
        del a
        def _take():
            if n < 1:
                return
            for _ in xrange(n):
                yield _builtin_next(coll)
        return _take()
    else:
    	raise TypeError("take takes either 1 or 2 arguments ({} given)".format(len(a)))

def comp(*fns):
    """
    Takes a set of functions and returns a fn that is the composition of those fns.  The returned fn takes a variable number of args, applies the rightmost of fns to the args, the next fn (right-to-left) to the result, etc.
    """
    countFns = len(fns)
    if countFns == 0:
        return identity
    elif countFns == 1:
        return fns[0]
    elif countFns == 2:
        f, g = fns
        def fn(*a, **kw):
            return f(g(*a, **kw))
        return fn
    else:   # 3..n args
        return reduce(comp, fns) # more than 1 item, so always starts with comp(1st, 2nd)-call

def completing(f, cf=identity):
    """
    Takes a reducing function f of 2 args and returns a fn suitable for
    transduce by adding an arity-1 signature that calls cf (default -
    identity) on the result argument.
    """
    def _completing(*a):
        if len(a) == 0:
            return f()
        elif len(a) == 1:
            x, = a
            return cf(x)
        elif len(a) == 2:
            x, y = a
            return f(x, y)
        else:
            raise TypeError("_completing takes either 0, 1 or 2 arguments ({} given)".format(len(a)))

    return _completing

def transduce(*a):
    """
    transduce(xform, f, coll)
    transduce(xform, f, init, coll)

    xform is a transducer.

    reduce with a transformation of f (xf). If init is not
    supplied, f() will be called to produce it. f should be a reducing
    step function that accepts both 1 and 2 arguments, if it accepts
    only 2 you can add the arity-1 with 'completing'. Returns the result
    of applying (the transformed) xf to init and the first item in coll,
    then applying xf to that result and the 2nd item, etc. If coll
    contains no items, returns init and f is not called. Note that
    certain transforms may inject or skip items.
    """
    if len(a) == 3:
        xform, f, coll = a
        coll = iter(coll)
        del a
        return transduce(xform, f, f(), coll)
    elif len(a) == 4:
        xform, f, init, coll = a
        coll = iter(coll)
        del a
    else:
        raise TypeError("transduce takes either 3 or 4 arguments ({} given)".format(len(a)))

    _f = xform(f)
    ret = reduce(_f, init, coll)
    return _f(ret)

def sequence(*a):
    """
    sequence(coll)
    sequence(xform, coll)
    sequence(xform, coll, *colls)

    FIXME: returns a generator for now i.s.o. a lazy-seq!
    FIXME: only (coll) and (xform, coll) arities are currently implemented!

    Coerces coll to a (possibly empty) sequence, if it is not already one.
    Will not force a lazy seq. (sequence None) yields an empty sequence,
    When a transducer is supplied, returns a lazy sequence of applications of
    the transform to the items in coll(s), i.e. to the set of first
    items of each coll, followed by the set of second
    items in each coll, until any one of the colls is exhausted.
    Any remaining items in other colls are ignored.

    The transform should accept number-of-colls arguments!
    """
    if len(a) == 1:
        coll, = a
        del a
        if coll is None:
            return (_ for _ in ())

        coll = iter(coll)
        return (_x for _x in coll)
    elif len(a) == 2:
        xform, coll = a
        del a
        coll = (_ for _ in ()) if coll is None else iter(coll)
        _output = []
        def _sequence_step(*a):
            if len(a) == 0:
                pass
            elif len(a) == 1:
                result, = a
                return result
            elif len(a) == 2:
                result, input_ = a
                append(_output, input_)
            else:
                raise TypeError("_sequence_step takes either 0, 1 or 2 arguments ({} given)".format(len(a)))

        def _():
            xf = xform(_sequence_step)
            for input_ in coll:
                maybe_reduced = xf(None, input_)
                if is_reduced(maybe_reduced):
                    break
                else:
                    for _o in _output:
                        yield _o
                    del _output[:]

            xf(None)
            for _o in _output:
                yield _o
            del _output[:]
        return _()
    else:
        raise TypeError("sequence takes either 1 or 2 arguments ({} given)".format(len(a)))
