"Janky code - if you use it you deserve what you get."

import ast
import linecache
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from textwrap import dedent
from token import LPAR, RPAR
from tokenize import tokenize
from typing import TypeVar

from jamjam._utils import raise_

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


def _calling_lines() -> _Lines:
    frame = sys._getframe(2)  # noqa: SLF001
    code = frame.f_code
    i = frame.f_lasti // 2
    r1, r2, c1, c2 = _getitem(code.co_positions(), i)
    if r1 is None or r2 is None or c1 is None or c2 is None:
        raise ValueError

    lines = linecache.getlines(code.co_filename)
    lines = _slice(lines, (r1, c1), (r2, c2))
    return lines


def textify(*args: object, **kwargs: object) -> str:
    "Return the arguments as their source text."
    _ = args, kwargs
    lines = _calling_lines()

    readline = (line.encode() for line in lines).__next__
    tokens = tokenize(readline)

    t1 = next(t for t in tokens if t.exact_type == LPAR)
    t2 = next(t for t in tokens if t.exact_type == RPAR)
    lines = _slice(lines, t1.end, t2.start)
    return "".join(lines)


def identify(v: T, /) -> tuple[str, T]:
    "Return the arg's source text & value."
    lines = _calling_lines()
    for node in ast.walk(ast.parse("".join(lines))):
        if isinstance(node, ast.Call):
            arg = node.args[0]
            return ast.unparse(arg), v
    raise AssertionError


@contextmanager
def capture() -> Iterator[str]:
    "De-dented source text of the 'captured' with block."
    frame = sys._getframe(2)  # noqa: SLF001
    code = frame.f_code
    i = frame.f_lasti // 2
    r1, _, c1, _ = _getitem(code.co_positions(), i)
    if r1 is None or c1 is None:
        raise ValueError

    lines = linecache.getlines(code.co_filename)
    node = next(
        n
        for n in ast.walk(ast.parse("".join(lines)))
        if isinstance(n, ast.With)
        and any(
            item.context_expr.lineno == r1
            and item.context_expr.col_offset == c1
            for item in n.items
        )
    )

    s = node.body[0]
    r1, c1 = s.lineno, s.col_offset

    s = node.body[-1]
    r2 = s.end_lineno or raise_()
    c2 = s.end_col_offset or raise_()

    line0, *lines = _slice(lines, (r1, c1), (r2, c2))
    yield line0 + dedent("".join(lines))
