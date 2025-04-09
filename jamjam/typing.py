"""Extensions to the typing library."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import update_wrapper
from inspect import get_annotations, signature
from typing import (
    Never,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    get_overloads,
)

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T")
_K = TypeVar("_K")
_V_co = TypeVar("_V_co", covariant=True)

Fn = Callable[_P, _R]
Map = Mapping[_K, _V_co]
Seq = Sequence[_V_co]
No = Never


class _ArgCopier(Protocol[_P]):
    def __call__(self, f: Fn[..., _R], /) -> Fn[_P, _R]: ...


def copy_args(f: Fn[_P, object], /) -> _ArgCopier[_P]:
    """Give (unenforced) signature of `f`."""

    def decorator(g: Fn[..., _R]) -> Fn[_P, _R]:
        g.__signature__ = signature(f)  # type: ignore[attr-defined]
        g.__annotations__ = get_annotations(f)
        return g

    return decorator


def copy_type(_: _T, /) -> Fn[[object], _T]:
    """Logically `copy_type(x)(y)` ⟺ `cast(type(x), y)`."""
    return lambda x: cast(_T, x)


def _overload_err(
    f: Fn[..., object],
    args: Seq[object],
    kwds: Map[str, object],
) -> TypeError:
    name = f"{f.__module__}.{f.__qualname__}"
    msg = f"No overload of {name} matches {args=}, {kwds=}."
    return TypeError(msg)


def check_overloads(func: Fn[_P, _R], /) -> Fn[_P, _R]:
    """Check calls match one of the overload signatures."""
    # TODO: add runtime type-checking?

    def new_func(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        for func_overload in get_overloads(func):
            s = signature(func_overload)
            try:
                bound_args = s.bind(*args, **kwargs)
            except TypeError:
                continue
            return func(
                *bound_args.args, **bound_args.kwargs
            )
        raise _overload_err(func, args, kwargs)

    update_wrapper(new_func, func)
    return new_func


def use_overloads(f: Fn[[], None], /) -> Fn[..., object]:
    """Use `@overload` bodies as the implementation of `f`.

    No (runtime) types checked, so signatures should not
    overlap even after stripping type hints.
    """
    # TODO: add runtime type-checking?

    def new_func(*args: object, **kwargs: object) -> object:
        for func_overload in get_overloads(f):
            s = signature(func_overload)
            try:
                bound = s.bind(*args, **kwargs)
            except TypeError:
                continue
            return func_overload(*bound.args, **bound.kwargs)
        raise _overload_err(f, args, kwargs)

    update_wrapper(new_func, f)
    return new_func
