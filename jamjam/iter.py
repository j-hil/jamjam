"""More tools for working with iterables.

Sometimes shamelessly taken or adapted from the venerable
``more-itertools`` package:
https://more-itertools.readthedocs.io/en/stable/index.html
"""

from __future__ import annotations

from collections import deque
from collections.abc import Set
from itertools import groupby

from jamjam._lib.typevars import K, R, T
from jamjam.typing import CanIter, Fn, Iter, Pair


def ordered_set(iterable: CanIter[T]) -> Set[T]:
    "Cheap implementation of an ordered set."
    return dict.fromkeys(iterable, 0).keys()


def split(
    it: CanIter[T], pred: Fn[[T]] = bool
) -> Pair[Iter[T]]:
    "Split ``it`` in two based on ``pred``."
    # similar to `more_itertools.partition`

    iterator = iter(it)
    good_q = deque[T]()
    bad_q = deque[T]()

    def splitter(
        ours: deque[T], theirs: deque[T], *, side: bool
    ) -> Iter[T]:
        while True:
            if ours:
                yield ours.popleft()
                continue

            try:
                v = next(iterator)
            except StopIteration:
                return
            if (not side) ^ bool(pred(v)):
                yield v
                continue
            theirs.append(v)

    goods = splitter(good_q, bad_q, side=True)
    bads = splitter(bad_q, good_q, side=False)
    return goods, bads


def gather(
    it: CanIter[T], by: Fn[[T], K], into: Fn[[Iter[T]], R]
) -> dict[K, R]:
    "Gather ``it`` into dict of choice type."
    # useful over plain dict(groupby(...)) as can return
    # dict[X, list] easily as oppose to dict[X, Iter]
    return {k: into(v) for k, v in groupby(it, by)}
