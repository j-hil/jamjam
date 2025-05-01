from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar, TypeAlias, overload


def test_callable_typing() -> None:
    Func: TypeAlias = Callable[[object, int], str]

    def use() -> Func:
        return lambda _1, _2: ""

    class A:
        # not all the same!
        func1: Func  # unbound
        func2 = use()  # bound  (not implicit classvar!)
        func3: ClassVar[Func]  # bound
        func4: ClassVar = use()  # unbound

    def _(a: A, s: str) -> None:
        s = a.func1(a, 1)
        s = a.func2(1)
        s = a.func3(1)
        s = a.func4(a, 1)

        _ = s


def test_descriptor_typing() -> None:
    class Getter:
        @overload
        def __get__(
            self, instance: A, owner: type, /
        ) -> str: ...

        @overload
        def __get__(
            self, instance: None, owner: type, /
        ) -> int: ...

        def __get__(
            self, instance: A | None, owner: type, /
        ) -> int | str:
            raise NotImplementedError

    def use() -> Getter:
        return Getter()

    class A:
        # surprisingly all the same
        func1a: Getter
        func1b = use()
        func1c = Getter()
        func2a: ClassVar[Getter]
        func2b: ClassVar = use()
        func2c: ClassVar = Getter()

    def _(a: A, s: str, i: int) -> None:
        s = a.func1a
        i = A.func1a

        s = a.func1b
        i = A.func1b

        s = a.func1c
        i = A.func1c

        s = a.func2a
        i = A.func2a

        s = a.func2b
        i = A.func2b

        s = a.func2c
        i = A.func2c

        _ = s, i


def test_ca() -> None:
    Func1: TypeAlias = Callable[[object, str], str]
    Func2: TypeAlias = Callable[[object, int], int]

    class Getter:
        @overload
        def __get__(
            self, instance: B, owner: type, /
        ) -> Func1: ...
        @overload
        def __get__(
            self, instance: None, owner: type, /
        ) -> Func2: ...
        def __get__(
            self, instance: B | None, owner: type, /
        ) -> Func1 | Func2:
            raise NotImplementedError

    def use() -> Getter:
        return Getter()

    class B:
        # surprisingly all the same
        func1a: Getter
        func1b = use()
        func1c = Getter()
        func2a: ClassVar[Getter]
        func2b: ClassVar = use()
        func2c: ClassVar = Getter()

    def _(a: B, s: str, i: int) -> None:
        s = a.func1a(object(), "")
        i = B.func1a(object(), 1)

        s = a.func1b(object(), "")
        i = B.func1b(object(), 1)

        s = a.func1c(object(), "")
        i = B.func1c(object(), 1)

        s = a.func2a(object(), "")
        i = B.func2a(object(), 1)

        s = a.func2b(object(), "")
        i = B.func2b(object(), 1)

        s = a.func2c(object(), "")
        i = B.func2c(object(), 1)

        _ = s, i
