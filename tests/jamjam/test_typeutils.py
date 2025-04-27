import inspect
from collections.abc import Callable
from typing import (
    Any,
    Literal,
    TypeAlias,
    assert_type,
    overload,
)

from pytest import raises

from jamjam.typing import (
    Check,
    Seq,
    copy_params,
    copy_type,
    typing_only,
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


def test_hint_has_instance() -> None:
    Option: TypeAlias = Literal[1, 2, 3]

    x: Literal[Option, 4]
    for x in (1, 2, 3, 4):
        if Check[Option].has_instance(x):
            assert_type(x, Option)
            assert x in (1, 2, 3)
        else:
            assert_type(x, Literal[4])
            assert x == 4


def test_typing_only() -> None:
    class B:
        def f(self) -> int:
            return 1

    class A(B):
        @typing_only
        def f(self) -> int:
            raise NotImplementedError

    assert A().f() == 1
