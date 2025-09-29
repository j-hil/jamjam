"Disgustingly janky code."

import linecache
import sys
from collections.abc import Iterable
from token import LPAR, RPAR
from tokenize import tokenize
from typing import TypeVar

T = TypeVar("T")
_Lines = list[str]
_Coord = tuple[int, int]


def _getitem(it: Iterable[T], i: int) -> T:
    it = iter(it)
    v = next(it)
    for _ in range(1, i):
        v = next(it)
    return v


def _slice(lines: _Lines, p: _Coord, q: _Coord) -> _Lines:
    r1, c1, r2, c2 = *p, *q
    if r1 == r2:
        return [lines[r1 - 1][c1:c2]]
    line1, *lines, line2 = lines[r1 - 1 : r2]
    lines = [line1[c1:], *lines, line2[:c2]]
    return lines


def textify(*args: object, **kwargs: object) -> str:
    "If you use this func you deserve what you get."
    _ = args, kwargs

    frame = sys._getframe(1)  # noqa: SLF001
    code = frame.f_code
    i = frame.f_lasti // 2
    r1, r2, c1, c2 = _getitem(code.co_positions(), i)
    if r1 is None or r2 is None or c1 is None or c2 is None:
        raise ValueError

    lines = linecache.getlines(code.co_filename)
    lines = _slice(lines, (r1, c1), (r2, c2))
    readline = (line.encode() for line in lines).__next__
    tokens = tokenize(readline)

    t1 = next(t for t in tokens if t.exact_type == LPAR)
    t2 = next(t for t in tokens if t.exact_type == RPAR)
    lines = _slice(lines, t1.end, t2.start)
    return "".join(lines)
