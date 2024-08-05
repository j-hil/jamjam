from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, ParamSpec, Protocol, TypeVar, overload

F = TypeVar("F", bound=Callable)
P = ParamSpec("P")


class Decorator(Protocol):
    """A signature preserving un-parameterized decorator."""

    def __call__(self, func: F, /) -> F: ...


@dataclass(frozen=True)
class Factory(Generic[P]):
    """A decorator factory."""

    implementation: Callable[P, Decorator]

    @overload
    def __call__(
        self, func: None = None, /, *args: P.args, **kwargs: P.kwargs
    ) -> Decorator: ...

    @overload
    def __call__(self, func: F, /, *args: P.args, **kwargs: P.kwargs) -> F: ...

    def __call__(
        self, func: F | None = None, /, *args: P.args, **kwargs: P.kwargs
    ) -> F | Decorator:
        if args:
            msg = "Either no args or only arg is decorated function."
            raise TypeError(msg)
        if func:
            return self.implementation(*args, **kwargs)(func)
        return self.implementation(*args, **kwargs)
