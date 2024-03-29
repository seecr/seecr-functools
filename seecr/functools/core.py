## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2017-2018, 2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

# from functools import reduce


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

_not_found = type('NOT_FOUND', (object,), {})()

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
        _1, _2 = next(coll, _not_found), next(coll, _not_found)
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
        _coll_items = zip(*map(iter, colls))
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
    _zipped_items = zip(*colls)
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

def iterate(f, x):
    while True:
        yield x
        x = f(x)

def first(iterable, default=None):
    if iterable:
        for v in iterable:
            return v
    return default

def second(iterable, default=None):
    if iterable:
        iterable = iter(iterable)
        next(iterable, None)
        return next(iterable, default)

    return default

def last(iterable, default=None):
    l = default
    if iterable:
        for l in iterable:
            pass

    return l

# TODO: nth, before, after, assoc / assoc_in, get / get_in

def get(o, key, default=None):
    """
    Returns the value in an associative structure (that implement __getitem__),
    where key is a key or index. Returns None if the key is not present,
    or the default value if supplied.
    """
    if o is None:
        return default
    try:
        return o[key]
    except (IndexError, KeyError):
        return default

def get_in(o, keypath, default=None):
    """
    Returns the value in a nested associative structure (that implement __getitem__),
    where keypath is a (possibly empty) iterable collection of keys. Returns None if the key
    is not present, or the default value if supplied.
    """
    if o is None:
        return default
    v = o
    for i, key in enumerate(keypath):
        if v is None:
            return default
        try:
            v = v[key]
        except (IndexError, KeyError):
            return default
        except TypeError as e:
            raise TypeError(str(e) + ' (on accessing %s in %s)' % (repr(keypath[:i+1]), repr(o)))
    return v


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

def assoc_when(d, k, v):
    "assoc-in only when v is not None"
    # TODO: support *kvs args too (as assoc does)
    if v is not None:
        return assoc(d, k, v)
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

def update_in_when(d, keypath, f, *args):
    """
    Same as update_in, but only updates the value at keypath (& create intermediate missing dicts) when the return value of f is not None.
    """
    v = get_in(d, keypath)
    r = f(v, *args)
    if r is None:
        return d
    return assoc_in(d, keypath, r)

def merge(*ds):
    """
    merge dictionaries left-to-right.
    """
    n = {}
    for d in ds:
        n.update(d)
    return n

def merge_with(f, *ds):
    """
    Merge dictionaries left-to-right, calling f with old and new value if the key already exists.
    """
    n = {}
    for d in ds:
        for k, v in d.items():
            if k in n:
                n[k] = f(n[k], v)
            else:
                n[k] = v
    return n

truthy = bool
def falsy(o):
    return not o

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

_pred_falsy = lambda obj: obj is False or obj is None
def any_fn(*fns):
    """
    Takes a set of fns and returns a function that returns the first "predicate" logical true value (not None or False) returned by one of its composing functions against all aguments given.
    """
    def _any_fn(*a, **kw):
        for fn in fns:
            res = fn(*a, **kw)
            if not _pred_falsy(res):
                return res

    return _any_fn

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
            for _ in range(n):
                try:
                    yield next(coll)
                except StopIteration:
                    return
        return _take()
    else:
    	raise TypeError("take takes either 1 or 2 arguments ({} given)".format(len(a)))

def drop(*a):
    """
    drop(n)
    drop(n, coll)

    Returns an iterable of all but the first n items in coll.
    Returns a stateful transducer when no collection is provided.
    """
    if len(a) == 1:
        n, = a
        del a
        def _drop_xf(rf):
            _nv = [n]
            def _drop_step(*a):
                if len(a) == 0:
                    return rf()
                elif len(a) == 1:
                    result, = a
                    return rf(result)
                elif len(a) == 2:
                    result, input_ = a
                    _n = _nv[0]
                    _nv[0] = _nn = _n - 1
                    if _n > 0:
                        return result
                    else:
                        return rf(result, input_)
            return _drop_step
        return _drop_xf
    elif len(a) == 2:
        n, coll = a[0], iter(a[1])
        del a
        def _drop():
            if n < 1:
                return coll
            try:
                for _ in range(n):
                    next(coll)
            except StopIteration:
                pass

            return coll
        return _drop()
    else:
    	raise TypeError("drop takes either 1 or 2 arguments ({} given)".format(len(a)))

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

# In time expose more functions based on usage. TODO
__all__ = ['assoc', 'get_in', 'update_in', 'assoc_in']
