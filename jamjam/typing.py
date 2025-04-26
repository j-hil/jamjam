"""Extensions to the typing library."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from functools import update_wrapper
from inspect import get_annotations, signature
from types import ModuleType
from typing import (
    Any,
    Concatenate,
    Never,
    Protocol,
    cast,
    get_overloads,
)
from typing_extensions import ParamSpec, TypeVar

from jamjam._lib.typevars import K, P, R, T, T_co, V_co

# TODO: default seq & map type-vars too? set auto-variance?
_DR = TypeVar("_DR", default=object)
_DP = ParamSpec("_DP", default=...)

Fn = Callable[_DP, _DR]  #:
Map = Mapping[K, V_co]  #:
Seq = Sequence[V_co]  #:
Module = ModuleType  #:
No = Never
"Alias of ``Never``."

# Abbreviating these was *hard*. Iter = Iterator won as
# Iterator is the base concept (tho not base class) and the
# `iter` func really should return `Iter`.
Iter = Iterator[T_co]  #:
CanIter = Iterable[T_co]  #:

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2", default=_T1)

Pair = tuple[_T1, _T2]
"Type of 2-tuple, with 2nd type defaulting to 1st."
MethodDef = Fn[Concatenate[T, P], R]
"Parameterized type for method definitions."


class ParamsCopier(Protocol[P]):
    "A func which copies params for static checkers."

    def __call__(self, f: Fn[..., R], /) -> Fn[P, R]: ...


def copy_params(f: Fn[P, object], /) -> ParamsCopier[P]:
    """Transfer static signature of one func to another.

    Does not enforce new signature. Best for tweaking output
    of functions without having to re-expose every argument.

    .. code-block::

        @copy_params(range)
        def sum_range(*args, **kwds) -> int:
            return sum(range(*args, **kwds))
    """

    def decorator(g: Fn[..., R]) -> Fn[P, R]:
        g.__signature__ = signature(f)  # type: ignore[attr-defined]
        g.__annotations__ = get_annotations(f)
        return g

    return decorator


def copy_type(v: T, /) -> Fn[[object], T]:
    "Create caster for ``type(v)``."
    _ = v
    return lambda x: cast(T, x)


def _overload_err(
    f: Fn, args: Seq[object], kwargs: Map[str, object]
) -> TypeError:
    name = f"{f.__module__}.{f.__qualname__}"
    msg = f"No overload of {name} for {args=}, {kwargs=}."
    return TypeError(msg)


def check_overloads(f: Fn[P, R], /) -> Fn[P, R]:
    "Check calls to ``f`` match an overload signatures."
    # TODO: add runtime type-checking?

    def new_func(*args: P.args, **kwargs: P.kwargs) -> R:
        for func_overload in get_overloads(f):
            s = signature(func_overload)
            try:
                bound_args = s.bind(*args, **kwargs)
            except TypeError:
                continue
            return f(*bound_args.args, **bound_args.kwargs)
        raise _overload_err(f, args, kwargs)

    update_wrapper(new_func, f)
    return new_func


def use_overloads(f: Fn[[], None], /) -> Fn[..., object]:
    """Use ``@overload`` bodies to implement of ``f``.

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


# TODO: improve return type
def get_hints(v: Fn | type | Module) -> dict[str, Any]:
    "Get a func/class/module's type-hints."
    return get_annotations(v, eval_str=True)
