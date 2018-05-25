from functools import partial

from seecr.functools.core import identity


# Mostly from https://gist.github.com/SegFaultAX/10941721 and ported from Clojure
def walk(inner, outer, coll):
    if isinstance(coll, list):
        return outer([inner(e) for e in coll])
    elif isinstance(coll, dict):
        return outer(dict([inner(e) for e in coll.iteritems()]))
    elif isinstance(coll, tuple):
        return outer(tuple(inner(e) for e in coll))
    elif isinstance(coll, set):
        return outer(set(inner(e) for e in coll))
    else:
        return outer(coll)

def prewalk(fn, coll):
    return walk(partial(prewalk, fn), identity, fn(coll))

def postwalk(fn, coll):
    return walk(partial(postwalk, fn), fn, coll)

def _():
    def prn(e):
        print "Walked:", e
        return e

    def prewalk_demo(coll):
        return prewalk(prn, coll)

    def postwalk_demo(coll):
        return postwalk(prn, coll)

    return prewalk_demo, postwalk_demo
prewalk_demo, postwalk_demo = _()
del _
