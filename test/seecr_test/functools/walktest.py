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



from unittest import TestCase
from seecr.test.io import stdout_replaced

from collections import Mapping
from copy import deepcopy

from seecr.functools.core import identity
from seecr.functools.walk import walk, prewalk, postwalk, prewalk_demo, postwalk_demo


class WalkTest(TestCase):
    def test_walk_identity_preserves(self):
        for coll in [
                None,
                1,
                "aap",
                [1, 2, 3],
                {"a": "b", 1: 2},
                (4, 5, 6),
                set([7, 8, 9])]:
            res = walk(identity, identity, deepcopy(coll))
            res2 = walk(inner=identity, outer=identity, coll=deepcopy(coll))
            self.assertEqual(type(res), type(coll))
            self.assertEqual(res, coll)
            self.assertEqual(res2, coll)

    def test_walk_builds_new_coll(self):
        coll = [1, 2]
        res = walk(identity, identity, coll)
        self.assertEqual([1, 2], res)
        self.assertFalse(res is coll)

    def test_walk_fns_outer(self):
        log_outer = []
        def outer(e):
            log_outer.append(e)
            return "replaced"

        self.assertEqual("replaced", walk(identity, outer, [1, 2]))
        self.assertEqual([[1, 2]], log_outer)

    def test_walk_fns_inner(self):
        log_inner = []
        def inner(e):
            log_inner.append(e)
            return e + 10

        self.assertEqual([11, 12], walk(inner, identity, [1, 2]))
        self.assertEqual([1, 2], log_inner)

    def test_walk_outer_after_inner(self):
        log = []
        def inner(e):
            log.append(("in", e))
            return e + 10
        def outer(e):
            log.append(("out", e))
            return set(e)

        self.assertEqual({11, 12}, walk(inner, outer, [1, 2]))
        self.assertEqual([("in", 1), ("in", 2), ("out", [11, 12])], log)

    def test_prewalk_visit_order(self):
        log = []
        def f(e):
            log.append(e)
            return e
        coll = [1, [22, 33], {"k": {"kk": ("v", "v2")}}, {"a",}]
        res = prewalk(f, deepcopy(coll))
        self.assertEqual(coll, res)
        self.assertEqual(
            [
                [1, [22, 33], {'k': {'kk': ('v', 'v2')}}, set(['a'])],
                1,
                [22, 33],
                22,
                33,
                {'k': {'kk': ('v', 'v2')}},
                ('k', {'kk': ('v', 'v2')}),
                'k',
                {'kk': ('v', 'v2')},
                ('kk', ('v', 'v2')),
                'kk',
                ('v', 'v2'),
                'v',
                'v2',
                set(['a']),
                'a',
            ],
            log)

    def test_postwalk_visit_order(self):
        log = []
        def f(e):
            log.append(e)
            return e
        coll = [1, [22, 33], {"k": {"kk": ("v", "v2")}}, {"a",}]
        res = postwalk(f, deepcopy(coll))
        self.assertEqual(coll, res)
        self.assertEqual(
            [
                1,
                22,
                33,
                [22, 33],
                'k',
                'kk',
                'v',
                'v2',
                ('v', 'v2'),
                ('kk', ('v', 'v2')),
                {'kk': ('v', 'v2')},
                ('k', {'kk': ('v', 'v2')}),
                {'k': {'kk': ('v', 'v2')}},
                'a',
                set(['a']),
                [1, [22, 33], {'k': {'kk': ('v', 'v2')}}, set(['a'])]
            ],
            log)

    def test_postwalk_example(self):
        def f(e):
            if isinstance(e, dict):
                return {}
            return e
        self.assertEqual([1, {}], postwalk(f, [1, {"k": "v"}]))

        with stdout_replaced() as out:
            postwalk_demo([1, {"k": "v"}])
            res = out.getvalue()

        self.assertEqual('''Walked: 1
Walked: k
Walked: v
Walked: ('k', 'v')
Walked: {'k': 'v'}
Walked: [1, {'k': 'v'}]\n''', res)

    def test_prewalk_example(self):
        def f(e):
            if isinstance(e, dict):
                return {}
            return e
        self.assertEqual([1, {}], prewalk(f, [1, {"k": "v"}]))

        with stdout_replaced() as out:
            prewalk_demo([1, {"k": "v"}])
            res = out.getvalue()

        self.assertEqual('''Walked: [1, {'k': 'v'}]
Walked: 1
Walked: {'k': 'v'}
Walked: ('k', 'v')
Walked: k
Walked: v\n''', res)

    def test_walk_supports_Mapping(self):
        class MyMapping(Mapping):
            def __getitem__(self, key):
                return 'aValue'
            def __iter__(self):
                yield 'aKey'
            def __len__(self):
                return 1
        m = MyMapping()
        res = walk(inner=lambda k_v: (k_v[0], '~' + k_v[1]), outer=identity, coll=m)
        self.assertEqual({'aKey': '~aValue'}, res)
