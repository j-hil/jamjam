"""More tools for working with iterables.

Sometimes shamelessly taken or adapted from the venerable
``more-itertools`` package:
https://more-itertools.readthedocs.io/en/stable/index.html
"""

from __future__ import annotations

from collections import deque
from collections.abc import Set
from itertools import groupby
from typing import TypeVar, overload

from jamjam.typing import (
    CanIter,
    Dots,
    Fn,
    Iter,
    Three,
    Two,
    use_overloads,
)

D = TypeVar("D")
K = TypeVar("K")
R = TypeVar("R")
T = TypeVar("T")


@overload
def first(it: CanIter[T]) -> T:
    return next(iter(it))


@overload
def first(it: CanIter[T], default: D) -> T | D:
    return next(iter(it), default)


@use_overloads
def first() -> None:
    "Get 1st item of ``it``, or ``default``."


def ordered_set(iterable: CanIter[T]) -> Set[T]:
    "Cheap implementation of an ordered set."
    return dict.fromkeys(iterable, 0).keys()


def split(
    it: CanIter[T], pred: Fn[[T]] = bool
) -> Two[Iter[T]]:
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


_Pattern3 = tuple[int, Dots, int]
_Pattern4 = tuple[int, int, Dots, int]
_Pattern = _Pattern3 | _Pattern4


class _IntegerIntervalFactory:
    @staticmethod
    def _parse_pattern(pattern: _Pattern) -> Three[int]:
        if len(pattern) == 4:
            start, second, _, end = pattern
            return start, end, second - start
        start, _, end = pattern
        return start, end, 1

    def __getitem__(self, pattern: _Pattern) -> range:
        start, end, sep = self._parse_pattern(pattern)
        return range(start, end + 1, sep)

    # Overloads only needed as unpack of union unsupported:
    # https://discuss.python.org/t/unpacking-a-union-of-tuples/52194
    @overload
    def __call__(self, *pattern: *_Pattern3) -> range: ...
    @overload
    def __call__(self, *pattern: *_Pattern4) -> range: ...
    def __call__(self, *pattern: *tuple) -> range:
        start, end, sep = self._parse_pattern(pattern)
        return range(start + sep, end, sep)


ii = _IntegerIntervalFactory()
"""Integer interval creation - alternate to ``range``.

Use ``ii(*pat)`` for exclusive interval, and ``ii[*pat]`` for
inclusive interval. ``pat`` can be ``(start, ..., end)`` for
increments of 1, or ``(start, second, ..., end)`` for
alternate step sizes.::

    r1 = ii(4, 8, ..., 20)
    assert list(r1) == [8, 12, 16]

    r2 = ii(4, ..., 8)
    assert list(r2) == [5, 6, 7]

    r3 = ii[4, 8, ..., 20]
    assert list(r3) == [4, 8, 12, 16, 20]

    r4 = ii[4, ..., 8]
    assert list(r4) == [4, 5, 6, 7, 8]

NOTE: This isn't exactly better than just using ``range``
directly but it was fun to write.
"""


@overload
def irange(start: int, stop: int, step: int = 1, /) -> range:
    return range(start, stop + 1, step)


@overload
def irange(stop: int, /) -> range:
    return range(stop + 1)


@use_overloads
def irange() -> None:
    "Inclusive range."
