## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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
