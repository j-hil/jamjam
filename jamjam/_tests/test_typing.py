import inspect
from collections.abc import Callable
from typing import Any, assert_type, overload

from pytest import raises

from jamjam.typing import (
    Seq,
    copy_params,
    copy_type,
    use_overloads,
)


def test_copy_signature() -> None:
    def f(x: int, y: Seq[int], *args: str, z: bool) -> float:
        _ = x, y, args, z
        return 10

    @copy_params(f)
    def g(*args: Any, **kwargs: Any) -> str:
        return str(f(*args, **kwargs))

    a = g(1, [], "", "", z=True)  # passes static check
    assert_type(a, str)  # keeps return type of original
    assert a == "10"

    with raises(TypeError, match=r"unexpected keyword"):
        _ = g(1, [], "", "", q=True)  # type: ignore[call-arg]

    assert inspect.signature(f) == inspect.signature(g)


def test_cope_type() -> None:
    @copy_type(hasattr)
    def noattr(*args: Any, **kwargs: Any) -> bool:
        return not hasattr(*args, **kwargs)

    assert_type(noattr, Callable[[object, str], bool])

    x = copy_type(1)("")  # can be used to lie
    assert_type(x, int)


def test_use_overloads() -> None:
    @overload
    def f(*, x: int, y: str) -> float:
        return x + int(y)

    @overload
    def f(*, x: str, z: str) -> str:
        return x + z

    @use_overloads
    def f() -> None: ...

    assert f(x=1, y="2") == 3
    assert f(x="a", z="b") == "ab"

    with raises(TypeError):
        f(z="a", y="b")  # type: ignore[call-overload]
