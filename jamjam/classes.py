"""Creation of custom classes."""

from typing import ClassVar, Self


class Singleton:
    """One instance per (sub)class."""

    _self: ClassVar[Self | None] = None

    def __new__(cls, *args: object, **kwds: object) -> Self:
        _ = args, kwds
        if not isinstance(cls._self, cls):
            cls._self = super().__new__(cls)
        return cls._self

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__}>"


def mk_repr(v: object, *args: object, **kwds: object) -> str:
    """Create a repr-like string for ``v`` using params."""
    cls_name = type(v).__qualname__
    body = ", ".join([
        *(str(arg) for arg in args),
        *(f"{kwd}={kwarg}" for kwd, kwarg in kwds.items()),
    ])
    return f"{cls_name}({body})"
