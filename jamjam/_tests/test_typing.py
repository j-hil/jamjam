import inspect
from typing import Any, assert_type

import pytest

from jamjam.typing import copy_signature


def test_copy_signature() -> None:
    def f(x: int, y: list[int], *args: str, z: bool) -> float:
        _ = x, y, args, z
        return 10

    @copy_signature(f)
    def g(*args: Any, **kwargs: Any) -> str:
        return str(f(*args, **kwargs))

    a = g(1, [], "", "", z=True)  # passes type check
    assert_type(a, str)  # keeps return type of original function
    assert a == "10"

    with pytest.raises(TypeError, match=r"unexpected keyword"):
        _ = g(1, [], "", "", q=True)  # type: ignore[call-arg]

    assert inspect.signature(f) == inspect.signature(g)
