from collections.abc import Callable
from typing import ClassVar, ParamSpec, Self, TypeVar


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
    body = ", ".join([
        *(str(arg) for arg in args),
        *(f"{kwd}={kwarg}" for kwd, kwarg in kwargs.items()),
    ])
    return f"{cls_name}({body})"


R = TypeVar("R")
P = ParamSpec("P")
Args_contra = TypeVar("Args_contra", contravariant=True, bound=object)


def expand(
    constructor: Callable[P, Args_contra],
) -> Callable[[Callable[[Args_contra], R]], Callable[P, R]]:
    """Define and implement a function using a class.

    Define a function who's signature is that of `constructor`.
    The function is implemented as a function
    with a single 'implementation' argument which is the value
    returned by passing the *user's* arguments to `constructor`.

    This creates a powerful way to manage 'families' of functions which
    share arguments, while maintaining type-safety and providing a natural
    way to re-use validation code or similar. This is most easily done using
    `dataclasses` or dataclass-like libraries. See examples.
    """
    # TODO: when you look at docs this is a good one to write up examples for
    # first. Also should this even be in the classes module?

    def decorator(func: Callable[[Args_contra], R]) -> Callable[P, R]:
        def new_func(*args: P.args, **kwargs: P.kwargs) -> R:
            implementation_arg = constructor(*args, **kwargs)
            return func(implementation_arg)

        return new_func

    return decorator
