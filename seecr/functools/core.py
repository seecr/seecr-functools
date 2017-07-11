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
