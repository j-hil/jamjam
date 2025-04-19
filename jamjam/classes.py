"""Creation of custom classes."""

from typing import ClassVar, Self, final
from typing_extensions import TypeIs


class Singleton:
    """One instance per (sub)class.

    Useful for private defaults when ``None`` unavailable::

        class _Missing(Singleton): ...


        def f(x: int | _Missing = _Missing()) -> None:
            if _Missing.is_(x):
                ...  # caller missed param
                return
            reveal_type(x)  # reveals `int`
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
