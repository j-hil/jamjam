from typing import ClassVar, Self


class Singleton:
    """A class with one instance; each subclass also gets one instance.

    I can't think of many good reasons to use a singleton but here is is anyway.
    A module usually serves the few valid use cases of a singleton well.
    Lazy constants and logging spring to mind.
    """

    _self: ClassVar[Self | None] = None

    def __new__(cls, *args: object, **kwargs: object) -> Self:
        _ = args, kwargs
        if not isinstance(cls._self, cls):
            cls._self = super().__new__(cls)
        return cls._self

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__}>"


def easy_repr(obj: object, *args: object, **kwargs: object) -> str:
    """Create a standard repr-like string for the given object."""
    cls_name = type(obj).__qualname__
    body = ",".join([
        *(str(arg) for arg in args),
        *(f"{kwd}={kwarg}" for kwd, kwarg in kwargs.items()),
    ])
    return f"{cls_name}({body})"
