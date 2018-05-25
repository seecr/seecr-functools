from __future__ import absolute_import

from unittest import TestCase
from seecr.test.io import stdout_replaced

from copy import deepcopy, copy

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
            self.assertEquals(type(res), type(coll))
            self.assertEquals(res, coll)
            self.assertEquals(res2, coll)

    def test_walk_builds_new_coll(self):
        coll = [1, 2]
        res = walk(identity, identity, coll)
        self.assertEquals([1, 2], res)
        self.assertFalse(res is coll)

    def test_walk_fns_outer(self):
        log_outer = []
        def outer(e):
            log_outer.append(e)
            return "replaced"

        self.assertEquals("replaced", walk(identity, outer, [1, 2]))
        self.assertEquals([[1, 2]], log_outer)

    def test_walk_fns_inner(self):
        log_inner = []
        def inner(e):
            log_inner.append(e)
            return e + 10

        self.assertEquals([11, 12], walk(inner, identity, [1, 2]))
        self.assertEquals([1, 2], log_inner)

    def test_walk_outer_after_inner(self):
        log = []
        def inner(e):
            log.append(("in", e))
            return e + 10
        def outer(e):
            log.append(("out", e))
            return set(e)

        self.assertEquals({11, 12}, walk(inner, outer, [1, 2]))
        self.assertEquals([("in", 1), ("in", 2), ("out", [11, 12])], log)

    def test_prewalk_visit_order(self):
        log = []
        def f(e):
            log.append(e)
            return e
        coll = [1, [22, 33], {"k": {"kk": ("v", "v2")}}, {"a",}]
        res = prewalk(f, deepcopy(coll))
        self.assertEquals(coll, res)
        self.assertEquals(
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
        self.assertEquals(coll, res)
        self.assertEquals(
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
        self.assertEquals([1, {}], postwalk(f, [1, {"k": "v"}]))

        with stdout_replaced() as out:
            postwalk_demo([1, {"k": "v"}])
            res = out.getvalue()

        self.assertEquals('''Walked: 1
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
        self.assertEquals([1, {}], prewalk(f, [1, {"k": "v"}]))

        with stdout_replaced() as out:
            prewalk_demo([1, {"k": "v"}])
            res = out.getvalue()

        self.assertEquals('''Walked: [1, {'k': 'v'}]
Walked: 1
Walked: {'k': 'v'}
Walked: ('k', 'v')
Walked: k
Walked: v\n''', res)
