from dataclasses import KW_ONLY, dataclass

import pytest

from jamjam.classes import Singleton, easy_repr, expand


def test_singleton() -> None:
    class A(Singleton):
        pass

    class B(Singleton):
        pass

    assert A() is A()
    assert B() is B()
    assert A() is not B()


def test_easy_repr() -> None:
    s = easy_repr("", 1, 2, hello=3, world=4)
    assert s == "str(1, 2, hello=3, world=4)"


def test_expand() -> None:
    @dataclass
    class SharedKwargs:
        _: KW_ONLY
        option1: str
        option2: str

    @dataclass
    class StrArgs(SharedKwargs):
        my_str: str

    @dataclass
    class IntArgs(SharedKwargs):
        my_int: int

    @expand(IntArgs)
    def convert_int(args: IntArgs) -> int:
        return args.my_int

    @expand(StrArgs)
    def convert_str(args: StrArgs) -> int:
        return int(args.my_str)

    assert convert_int(1, option1="", option2="") == 1
    assert convert_str("100", option1="", option2="") == 100

    with pytest.raises(TypeError):
        convert_str([], option1="", option2="")  # type: ignore[arg-type]
