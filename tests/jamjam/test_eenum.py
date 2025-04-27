from dataclasses import dataclass
from typing import Self, final

import pytest

from jamjam.eenum import Auto, EnumMixin, enum


def test_enum() -> None:
    @enum  # we are *stacked* 💪
    @final
    @dataclass(frozen=True)
    class MyEnum(EnumMixin):
        info: str

        @classmethod
        def _create_next_(
            cls, i: int, name: str, prev: tuple[Self, ...]
        ) -> Self:
            info = f"member {i}: {name}. {prev=}"
            return cls(info)

        A, B, C = Auto[Self].enumeral_list(3)

    assert tuple(MyEnum.iter()) == (
        MyEnum.A,
        MyEnum.B,
        MyEnum.C,
    )
    assert isinstance(MyEnum.A, MyEnum)

    with pytest.raises(
        TypeError, match=r"Cannot subclass enum-type"
    ):

        class _(MyEnum): ...  # type: ignore[misc]

    with pytest.raises(TypeError, match=r"Cannot make new"):
        MyEnum("hello")

    assert MyEnum("member 0: A. prev=()") is MyEnum.A


def test_no_members() -> None:
    with pytest.raises(TypeError, match=r"no enum-member"):

        @enum
        class _:
            @classmethod
            def _create_next_(cls, *_: object) -> Self:
                return cls()


def test_not_final() -> None:
    with pytest.raises(
        TypeError, match=r"mark .* with `@final`"
    ):
        # not allowed as using `Self` without `@final`
        @enum
        class _:
            @classmethod
            def _create_next_(cls, *_: object) -> Self:
                return cls()

            A, B = Auto[Self].enumeral_list(2)

    # ok as using `'MyEnum'` for the hint
    @enum
    class MyEnum:
        @classmethod
        def _create_next_(cls, *_: object) -> Self:
            return cls()

        A, B = Auto["MyEnum"].enumeral_list(2)

    assert isinstance(MyEnum.A, MyEnum)


def test_subclassing() -> None:
    @enum
    class MyEnum(int):
        @classmethod
        def _create_next_(cls, i: int, *_: object) -> Self:
            return cls(i)

        A, B = Auto["MyEnum"].enumeral_list(2)

    assert isinstance(MyEnum.A, MyEnum)
    assert isinstance(MyEnum.A, int)


def test_class_iter() -> None:
    @enum  # we are *stacked* 💪
    @final
    @dataclass
    class MyEnum:
        info: str

        @classmethod
        def _create_next_(
            cls, i: int, name: str, prev: tuple[Self, ...]
        ) -> Self:
            info = f"member {i}: {name}. {prev=}"
            return cls(info)

        iter = Auto[Self].give_class_iter()
        A, B, C = Auto[Self].enumeral_list(3)

    assert isinstance(MyEnum.A, MyEnum)
    assert list(MyEnum.iter()) == [
        MyEnum.A,
        MyEnum.B,
        MyEnum.C,
    ]


def test_proto_repr() -> None:
    class Base:
        def __repr__(self) -> str:
            return "X"

    class CustomEnumMixin(Base):
        @classmethod
        def _create_next_(
            cls, i: int, name: str, prev: tuple[Self, ...]
        ) -> Self:
            return cls()

        __repr__ = Auto[Self].give_repr()

    mixin = (
        CustomEnumMixin()
    )  # shouldn't do this but i guess it could happen
    assert (
        repr(mixin) == "X"
    )  # and if it does the parent repr is used

    @enum
    @final
    class MyEnum(CustomEnumMixin):
        A = Auto[Self].enumeral()

    assert (
        repr(MyEnum.A)
        == "<test_proto_repr.<locals>.MyEnum.A>"
    )


def test_unpacking() -> None:
    @enum
    @final
    @dataclass
    class MyEnum(EnumMixin):
        i: int
        name: str
        prev: tuple[Self, ...]

        @classmethod
        def _create_next_(cls, i, name, prev):
            return cls(i, name, prev)

        A, B, *CDE, F = Auto[Self].enumeral_list(6)

    MyEnum.CDE
