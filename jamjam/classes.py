"""Creation of custom classes."""

from collections.abc import Iterator
from enum import auto
from typing import (
    ClassVar,
    Protocol,
    Self,
    TypeVar,
    final,
    overload,
)
from typing_extensions import TypeIs

from jamjam._lib.typevars import T

O_con = TypeVar("O_con", contravariant=True)
OT = TypeVar("OT", bound=type[O_con])
Ob = object


# TODO: all of this.
class CompleteDescriptor(Protocol[O_con]):
    def __set_name__(
        self, owner: type[O_con], name: str, /
    ) -> None:
        return

    @overload
    def __get__(
        self, v: None, owner: type[O_con] | None = None, /
    ) -> Ob: ...
    @overload
    def __get__(
        self, v: O_con, vt: type[O_con] | None = None, /
    ) -> Ob: ...

    def __set__(self, v: O_con, value: Ob, /) -> None:
        msg = f"Can't set member {self} of object {v}"
        raise AttributeError(msg)

    def __delete__(self, obj: O_con, /) -> None:
        return


@overload
def auto_batch(n: int, /) -> Iterator[auto]: ...
@overload
def auto_batch(
    arg0: int, arg1: int, /, *args: int
) -> Iterator[Iterator[auto]]: ...


def auto_batch(
    n: int, /, *args: int
) -> Iterator[Iterator[auto]] | Iterator[auto]:
    """Assign many enum members with ``auto()`` at once.

    For example::

        class Value(Enum):
            value: int  # optionally re-declare for type-checkers
            A, B, C = auto_batch(3)

    And multiple lines of values::

        class Alphabet(StrEnum):
            value: str
            (
                (
                    A,
                    B,
                    C,
                    D,
                    E,
                    F,
                    G,
                    H,
                    I,
                    J,
                    K,
                    L,
                    M
                ),
                (N, 0, P, Q, R, S, T, U, V, W, X, Y, Z),
            ) = auto_batch(16, 10)

    For simple integer members using ``range`` may be preferred.
    """
    if not args:
        return (auto() for _ in range(n))
    args = (n, *args)
    return ((auto() for _ in range(n)) for n in args)


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
