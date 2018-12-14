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

"""
Wrangling data fns.
"""

from seecr.functools.core import fpartial


def fix(x, *clauses):           # similar to: https://github.com/amalloy/useful flatland.useful.fn/fix
    """
    Walk through clauses, a series of predicate/transform pairs. The
    first predicate that x satisfies has its transformation clause
    called on x. Predicates or transforms may be values (eg True or None)
    rather than functions; these will be treated as functions that
    return that value.

    The last "pair" may be only a transform with no pred: in that case it
    is unconditionally used to transform x, if nothing previously matched.
    If no predicate matches, then x is returned unchanged.
    """
    if not clauses:
        return x

    remaining = list(clauses)
    while remaining:
        if len(remaining) == 1:
            fn = remaining[0]
            return fn(x) if callable(fn) else fn

        test, fn, remaining = remaining[0], remaining[1], remaining[2:]
        if (test(x) if callable(test) else test): # test | test(x) -> truthyness!
            return (fn(x) if callable(fn) else fn)

    return x

def to_fix(*clauses):           # similar to: https://github.com/amalloy/useful flatland.useful.fn/to-fix
    """
    A "curried" version of fix, which sets the clauses once, yielding a
    function that calls fix with the specified first argument.
    """
    return fpartial(fix, *clauses)
