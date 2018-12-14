
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

def map(f):
    """
    FIXME: Only transducer-arity implemented!

    Returns a lazy sequence consisting of the result of applying f to
    the set of first items of each coll, followed by applying f to the
    set of second items in each coll, until any one of the colls is
    exhausted.  Any remaining items in other colls are ignored. Function
    f should accept number-of-colls arguments. Returns a transducer when
    no collection is provided.
    """
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

def filter(pred):
    """
    FIXME: Only transducer-arity implemented!

    Returns a lazy sequence of the items in coll for which
    (pred item) returns true. pred must be free of side-effects.
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
    (pred item) returns false. pred must be free of side-effects.
    Returns a transducer when no collection is provided.
    """
    return filter(complement(pred))

def first(iterable):
    if iterable:
        for v in iterable:
            return v

def second(iterable):
    if iterable:
        iterable = iter(iterable)
        next(iterable, None)
        return next(iterable, None)

# TODO: nth, before, after, assoc / assoc_in, get / get_in

def identity(x):
    return x

def complement(f):
    """
    Takes a fn f and returns a fn that takes the same arguments as f,
    has the same effects, if any, and returns the opposite truth value.
    """
    def _complement(*a, **kw):
        return not f(*a, **kw)
    return _complement

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
                yield next(coll)
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

    reduce with a transformation of f (xf). If init is not
    supplied, (f) will be called to produce it. f should be a reducing
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
