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

_F = TypeVar("_F", bound=Fn)
_P = ParamSpec("_P")
_R = TypeVar("_R")
_T_co = TypeVar("_T_co", covariant=True)
_T_con = TypeVar("_T_con", contravariant=True)


class Decorator(Protocol):
    """A signature preserving un-parameterized decorator."""

    def __call__(self, f: _F, /) -> _F: ...


class DecoratorFactory(Generic[_P]):
    """Add standard behaviors to simple decorator factories.

    For a factory that returns simple decorators (i.e. a
    parameterized decorator), this adds the ability to make
    calls in the standard ways; ``@decorator``,
    ``@decorator(...)`` and ``f = decorator(f, ...)``.

    Most appropriate for factories with kwargs-only and
    fully defaulted signatures.
    """

    __wrapped__: Fn[_P, Decorator]

    def __init__(self, f: Fn[_P, Decorator]) -> None:
        update_wrapper(self, f)

    @overload
    def __call__(
        self,
        f: None = None,
        /,
        *args: _P.args,
        **kwds: _P.kwargs,
    ) -> Decorator: ...

    @overload
    def __call__(
        self, f: _F, /, *args: _P.args, **kwargs: _P.kwargs
    ) -> _F: ...

    def __call__(
        self,
        f: _F | None = None,
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _F | Decorator:
        decorator = self.__wrapped__(*args, **kwargs)
        if f is None:
            return decorator
        return decorator(f)


class _Expander(Protocol[_T_co, _P]):
    def __call__(
        self, f: Fn[[_T_co], _R], /
    ) -> Fn[_P, _R]: ...


def expand(cls: Fn[_P, _T_con]) -> _Expander[_T_con, _P]:
    """Define and implement a function using a class.

    Define a func with signature matching ``cls.__new__``.
    The decorated function is implemented with 1 arg;
    this arg is constructed by passing the callers
    args into ``cls``.
    """

    def decorator(f: Fn[[_T_con], _R]) -> Fn[_P, _R]:
        def g(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            arg = cls(*args, **kwargs)
            return f(arg)

        return g

    return decorator
