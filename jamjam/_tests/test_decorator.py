from typing import assert_type

import pytest

from jamjam import decorator


def test_basic_factory() -> None:
    @decorator.Factory
    def my_decorator(*, x: int = 1, y: str = "") -> decorator.Decorator:
        _ = x, y
        return lambda f: f

    @my_decorator(x=1)
    def f(p: str) -> int:
        return int(p)

    a = f("111")
    assert_type(a, int)
    assert a == 111

    with pytest.raises(TypeError):
        _ = f([])  # type: ignore[arg-type]

    @my_decorator
    def g(q: list[str]) -> str:
        return q[0]

    b = g(["hey"])
    assert_type(b, str)
    assert b == "hey"

    def h(r: int) -> list[int]:
        return [r]

    h = my_decorator(h, y="")

    c = h(1)
    assert_type(c, list[int])
    assert c == [1]
