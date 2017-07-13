
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

_not_found = type('NOT_FOUND', (object,), {})()

def reduce(*args):
    """
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

    reduce(f, coll)
    reduce(f, val, coll)
    """
    if len(args) == 2:
        f, coll = args[0], iter(args[1])
        _1, _2 = next(coll, _not_found), next(coll, _not_found)
        if _1 is _not_found:
            return f()
        elif _2 is _not_found:
            return _1

        accum_value = f(_1, _2)
    elif len(args) == 3:
        f, val, coll = args
        accum_value = val
    else:
        raise TypeError("reduce takes either 2 or 3 arguments ({} given)".format(len(args)))

    for x in coll:
        accum_value = f(accum_value, x)
        if is_reduced(accum_value):
            return accum_value.val
    return accum_value

##

def first(iterable):
    if iterable:
        for v in iterable:
            return v

def second(iterable):
    if iterable:
        for i, v in enumerate(iterable):
            if i == 1:
                return v

def identity(x):
    return x

def some_thread(x, *fns):
    ""
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




def transduce(*args):
    """
    reduce with a transformation of f (xf). If init is not
    supplied, (f) will be called to produce it. f should be a reducing
    step function that accepts both 1 and 2 arguments, if it accepts
    only 2 you can add the arity-1 with 'completing'. Returns the result
    of applying (the transformed) xf to init and the first item in coll,
    then applying xf to that result and the 2nd item, etc. If coll
    contains no items, returns init and f is not called. Note that
    certain transforms may inject or skip items.

    xform = comp of fns
    f = f(1, 2) or f(1)
    init = inital value (optional)
    coll = iterable data (string not advised)
    """

    xform = f = coll = init = None
    if len(args) == 3:
        xform, f, coll = args
        return transduce(xform, f, f(), coll)

    elif len(args) == 4:
        xform, f, init, coll = args
        f = xform(f)

     # (let [f (xform f)
     #       ret (if (instance? clojure.lang.IReduceInit coll)
     #             (.reduce ^clojure.lang.IReduceInit coll f init)
     #             (clojure.core.protocols/coll-reduce coll f init))]
     #   (f ret))))

def _transduce(xform, f, coll, init=None):
    if init:
        pass
