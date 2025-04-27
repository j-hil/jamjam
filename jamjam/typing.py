"""More typing extensions: 'I will square this circle' - ⏺️."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from functools import update_wrapper
from inspect import get_annotations, signature
from types import ModuleType, UnionType
from typing import (
    Any,
    Concatenate,
    Generic,
    Literal,
    Never,
    Protocol,
    Self,
    cast,
    get_args,
    get_overloads,
)
from typing_extensions import TypeIs, ParamSpec, TypeVar

from jamjam._lib.typevars import F, K, P, R, T

_DR = TypeVar("_DR", default=object)
_DP = ParamSpec("_DP", default=...)
_DV_co = TypeVar("_DV_co", default=object, covariant=True)
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2", default=_T1)

LiteralType = type(Literal[1])
ProtocolMeta = type(Protocol)


Fn = Callable[_DP, _DR]  #:
Map = Mapping[K, _DV_co]  #:
Seq = Sequence[_DV_co]  #:
Module = ModuleType
"Default type of any module."
No = Never
"Alias of ``Never``."

Hint = type[object] | UnionType
"""Type of any (non-str) type-hint.

NOTE: isn't complete & may be impossible to do so.
"""

# Abbreviating these was *hard*. Iter = Iterator won as
# Iterator is the base concept (tho not base class) and the
# `iter` func really should return `Iter`.
Iter = Iterator[_DV_co]  #:
CanIter = Iterable[_DV_co]  #:

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


def _ol_ex(f: Fn, args: Seq, kwds: Map[str]) -> TypeError:
    name = f"{f.__module__}.{f.__qualname__}"
    msg = f"No overload of {name} for {args=}, {kwds=}."
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
        raise _ol_ex(f, args, kwargs)

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
        raise _ol_ex(f, args, kwargs)

    update_wrapper(new_func, f)
    return new_func


def get_hints(v: Fn | type | Module) -> dict[str, Hint]:
    "Get a func/class/module's type-hints."
    return get_annotations(v, eval_str=True)


def copy_method_signature(
    typed: Callable[Concatenate[Any, P], object],
) -> Callable[[Callable[..., R]], Callable[P, R]]:
    _ = typed  # TODO: extract the relevant info from `typed` at runtime
    return lambda x: x


class _Delete:
    """Descriptor which deletes itself as soon as it's assigned."""

    def __init__(self, _: object) -> None: ...

    def __set_name__(self, v: type, name: str) -> None:
        delattr(v, name)


def typing_only(func: F) -> F:
    """Make a method only available to a type-checker."""
    return _Delete(func)  # type: ignore[return-value]  # obvious lie


# def _add_repr(cls: _HintTypeT) -> _HintTypeT:
#     def __repr__(self: _HintTypeT) -> str:
#         # return f"{self.__qualname__}[{self._hint}]"
#         return "100"
#     # object.__setattr__(cls.__class__, "__repr__", __repr__)
#     # cls.__class__.__repr__ = (__repr__)
#     return cls
_missing: Any = object()


class Hint(Generic[T]):
    """Raise a type hints out of annotations & into runtime code.

    Through this class any hint can we manipulated at runtime inside of
    class methods, *without* requiring the loss of it's information to the
    type-checker.
    """

    # classvar, but can't use ClassVar[...] due to type var
    _hint: type[T] = _missing

    @classmethod
    def get_hint(cls) -> type[T]:
        # provides access to type-hint without type-checkers complaining
        # and providing a better message when hint is not set.
        hint = cls._hint
        if hint is _missing:
            msg = f"{cls.__name__} is un-parameterized so has no hint."
            raise TypeError(msg)
        return cls._hint

    @abstractmethod
    def _do_not_instantiate_(self) -> Never: ...

    def __init_subclass__(
        cls, *, _hint: type[T] = _missing, **kwargs: object
    ) -> None:
        cls._hint = _hint
        return super().__init_subclass__(**kwargs)

    def __class_getitem__(cls, hint: Any) -> type[Self]:
        if isinstance(hint, tuple):
            msg = "Only one type parameter allowed."
            raise TypeError(msg)
        return type("HintAlias", (cls,), {}, _hint=hint)


class Check(Hint[T]):
    """Generalized isinstance checks & similar."""

    @classmethod
    def has_instance(cls, obj: object) -> TypeIs[T]:
        hint = cls._hint
        if isinstance(hint, type | UnionType | ProtocolMeta):
            return isinstance(obj, hint)

        # TODO: i don't think this works properly - probs just is isinstance(..., func)
        # probs need to switch to get_origin etc
        if isinstance(hint, LiteralType):
            return obj in get_args(hint)
        msg = f"Type-hint {hint} is not supported."
        raise NotImplementedError(msg)


def maybe(_: type[T], /) -> T | None:
    return None
