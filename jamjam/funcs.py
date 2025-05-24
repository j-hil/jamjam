"""Easily create type-safe decorators."""

from __future__ import annotations

from functools import update_wrapper
from typing import (
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)

from jamjam.typing import Fn

F = TypeVar("F", bound=Fn)
P = ParamSpec("P")
R = TypeVar("R")
C = TypeVar("C", covariant=True)
T = TypeVar("T", contravariant=True)


class Decorator(Protocol):
    """A signature preserving un-parameterized decorator."""

    def __call__(self, f: F, /) -> F: ...


class DecoratorFactory(Generic[P]):
    """Add standard behaviors to simple decorator factories.

    For a factory that returns simple decorators (i.e. a
    parameterized decorator), this adds the ability to make
    calls in the standard ways; ``@decorator``,
    ``@decorator(...)`` and ``f = decorator(f, ...)``.

    Most appropriate for factories with kwargs-only and
    fully defaulted signatures.
    """

    __wrapped__: Fn[P, Decorator]

    def __init__(self, f: Fn[P, Decorator]) -> None:
        update_wrapper(self, f)

    @overload
    def __call__(
        self,
        f: None = None,
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Decorator: ...

    @overload
    def __call__(
        self, f: F, /, *args: P.args, **kwds: P.kwargs
    ) -> F: ...

    def __call__(
        self,
        f: F | None = None,
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> F | Decorator:
        decorator = self.__wrapped__(*args, **kwds)
        if f is None:
            return decorator
        return decorator(f)


class _Expander(Protocol[C, P]):
    def __call__(self, f: Fn[[C], R], /) -> Fn[P, R]: ...


def expand(cls: Fn[P, T]) -> _Expander[T, P]:
    """Define and implement a function using a class.

    Define a func with signature matching ``cls.__new__``.
    The decorated function is implemented with 1 arg;
    this arg is constructed by passing the callers
    args into ``cls``.
    """

    def decorator(f: Fn[[T], R]) -> Fn[P, R]:
        def g(*args: P.args, **kwargs: P.kwargs) -> R:
            arg = cls(*args, **kwargs)
            return f(arg)

        return g

    return decorator
