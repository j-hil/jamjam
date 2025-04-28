"""Creation of custom classes."""

from enum import auto
from typing import ClassVar, Protocol, Self, final, overload
from typing_extensions import TypeIs

from jamjam._lib.typevars import T, X
from jamjam.typing import Iter


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
