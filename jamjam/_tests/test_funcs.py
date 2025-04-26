from dataclasses import KW_ONLY, dataclass
from typing import assert_type

import pytest

from jamjam.funcs import Decorator, DecoratorFactory, expand


def test_factory() -> None:
    @DecoratorFactory
    def my_decorator(x: int = 1, y: str = "") -> Decorator:
        _ = x, y
        return lambda f: f

    implementation = my_decorator.__wrapped__
    assert implementation.__name__ == "my_decorator"

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
        return f"0th element: {q[0]}"

    b = g(["hey"])
    assert_type(b, str)
    assert b == "0th element: hey"

    def h(r: int) -> list[int]:
        return [r]

    h = my_decorator(h, y="")

    c = h(1)
    assert_type(c, list[int])
    assert c == [1]


def test_expand() -> None:
    @dataclass
    class BaseArgs:
        _: KW_ONLY
        option1: str
        option2: str

    @dataclass
    class StrArgs(BaseArgs):
        my_str: str

    @dataclass
    class IntArgs(BaseArgs):
        my_int: int

    @expand(IntArgs)
    def make_int(args: IntArgs) -> int:
        return args.my_int

    @expand(StrArgs)
    def make_str(args: StrArgs) -> int:
        return int(args.my_str)

    assert make_int(1, option1="", option2="") == 1
    assert make_str("100", option1="", option2="") == 100

    with pytest.raises(TypeError):
        make_str([], option1="", option2="")  # type: ignore[arg-type]
