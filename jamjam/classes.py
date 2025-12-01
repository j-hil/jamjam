"""Creation of custom classes."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from enum import auto
from typing import (
    ClassVar,
    Generic,
    Protocol,
    Self,
    final,
    overload,
)
from typing_extensions import TypeIs, TypeVar

from jamjam._utils import unwrap
from jamjam.typing import Iter

IR = TypeVar("IR", covariant=True)
T = TypeVar("T", default=object)
X = TypeVar("X", contravariant=True)


class Singleton:
    """One instance per (sub)class.

    Useful for private defaults when ``None`` unavailable::

        class _Missing(Singleton): ...


        def f(x: int | _Missing = _Missing()) -> None:
            if _Missing.is_(x):
                ...  # caller missed param
                return
            reveal_type(x)  # reveals ``int``
    """

    _self: ClassVar[Self | None] = None

    @final
    def __new__(cls) -> Self:
        if not isinstance(cls._self, cls):
            cls._self = super().__new__(cls)
        return cls._self

    @classmethod
    def is_(cls, v: object) -> TypeIs[Self]:
        "Check ``v`` is the singleton, with static support."
        return cls() is v

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__}>"


def mk_repr(v: object, *args: object, **kwds: object) -> str:
    "Create a repr-like string for ``v`` using params."
    cls_name = type(v).__qualname__
    body = ", ".join([
        *(str(arg) for arg in args),
        *(f"{kwd}={kwarg}" for kwd, kwarg in kwds.items()),
    ])
    return f"{cls_name}({body})"


def mk_subtype(name: str, base: type[T]) -> type[T]:
    "Create 'empty' subtype using ``base`` as only parent."
    return type(name, (base,), {})


def autos(n: int, /) -> Iter[auto]:
    "Assign many enum members with ``auto()`` at once."
    return (auto() for _ in range(n))


# Currently more reference snippet than anything practical.
class FullDescriptor(Protocol[X]):
    "https://docs.python.org/3/howto/descriptor.html"

    def __set_name__(self, t: type[X], name: str, /) -> None:
        return

    @overload
    def __get__(self, x: None, t: type[X], /) -> object:
        "Invocation from a class; ``type(v).name``."

    @overload
    def __get__(self, x: X, t: type[X], /) -> object:
        "Invocation from an instance; ``v.name,``"

    @overload
    def __get__(self, x: X, t: None = None, /) -> object:
        "So called 'direct' invocation; ``d.__get__(x)``."

    def __get__(
        self, x: X | None, t: type[X] | None = None
    ) -> object:
        msg = f"Can't get member {self} of object {x}"
        raise AttributeError(msg)

    def __set__(self, x: X, value: object, /) -> None:
        msg = f"Can't set member {self} of object {x}"
        raise AttributeError(msg)

    def __delete__(self, x: X, /) -> None:
        return


class EzGetDesc(ABC, Generic[IR, T]):
    """Easy 'getter' descriptor creation.

    For descriptor decorators use with ``MethodDef`` like::
        class Desc(Generic[IR, T, P, R], EzGetDesc[IR, T]):
            def __init__(
                self, f: MethodDef[T, P, R]
            ) -> None:
                self.f = f

    Then when used like so::
        class A:
            @Desc
            def desc(self) -> int: ...

    we'll have T, P & R bound to A, [], and int respectively.
    I don't think this can be put in a re-usable class
    while retaining it's typing.
    """

    __owner: type[T] | None = None
    __name: str | None = None

    def __set_name__(self, t: type[T], name: str, /) -> None:
        self.__owner = t
        self.__name = name

    @final
    @property
    def __name__(self) -> str:
        if self.__name is None:
            msg = f"{self} not yet assigned to class."
            raise RuntimeError(msg)
        return self.__name

    @final
    @property
    def __owner__(self) -> type[T]:
        if self.__owner is None:
            msg = f"{self} not yet assigned to class."
            raise RuntimeError(msg)
        return self.__owner

    @overload
    def __get__(self, x: None, t: type[T], /) -> Self: ...
    @overload
    def __get__(self, x: T, t: type[T], /) -> IR: ...
    @overload
    def __get__(self, x: T, t: None = None, /) -> IR: ...
    def __get__(
        self, x: T | None, t: type[T] | None = None, /
    ) -> IR | Self:
        if x is not None:
            return self.instance_get(x)
        if t is not None:
            return self
        raise NotImplementedError

    @abstractmethod
    def instance_get(self, x: T, /) -> IR:
        "Invocation from an instance; ``x.name,``"
        raise NotImplementedError


class _DataModel:
    "https://docs.python.org/3/reference/datamodel.html"

    count: ClassVar = 0

    def __init__(self) -> None:
        type(self).count += 1
        self.position = self.count
        self.stream = sys.stdout

    def __invert__(self) -> _DataModel:
        msg = unwrap("""
            ~ is implemented with `__invert__`. Generally it
            should return an instance of the same class as
            self, or a parent.
            """)
        self.stream.write(msg + "\n")
        return _DataModel()

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.position})"


MAGIC_HELPER = _DataModel()
"Interactive object for reminders about python's data model."
