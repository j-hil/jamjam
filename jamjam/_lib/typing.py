from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def copy_signature(
    typed: Callable[P, object],
) -> Callable[[Callable[..., R]], Callable[P, R]]:
    """Apply the signature of `typed` to the decorated function.

    The new signature is not enforced.
    """

    def decorator(f: Callable[..., R]) -> Callable[P, R]:
        f.__signature__ = inspect.signature(typed)  # type: ignore[attr-defined]
        f.__annotations__ = inspect.get_annotations(typed)
        return f

    return decorator


T = TypeVar("T")


def copy_type(_: T) -> Callable[[Any], T]:
    return lambda x: x
