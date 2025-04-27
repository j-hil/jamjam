from collections import defaultdict

import pytest


def test_closing_over_default_factory() -> None:
    """Want to subclass with while 'fixing' the default factory."""
    key = ""
    Base = defaultdict[str, list[int]]

    class D1(Base):
        def __missing__(self, k: str) -> list[int]:
            return []

    d1 = D1()
    assert d1[key] is not d1[key]

    # so we need to set the value ourself
    class D2(Base):
        def __missing__(self, k: str) -> list[int]:
            self[k] = []
            return self[k]

    d2 = D2()
    assert d2[key] is d2[key]

    # but far simpler is to just set default_factory
    class D3(Base):
        def __init__(self) -> None:
            super().__init__(list)

    d3 = D3()
    assert d3[key] is d3[key]


def test_pop() -> None:
    d = defaultdict[str, list[int]](list)

    with pytest.raises(KeyError):
        d.pop("")  # default not created by pop
