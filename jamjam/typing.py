"Extensions to the typing library. Square this circle ⏺️."

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
from types import EllipsisType, ModuleType, UnionType
from typing import (
    Any,
    Concatenate,
    Generic,
    Literal,
    Never,
    Protocol,
    Self,
    Union,
    cast,
    get_args,
    get_origin,
    get_overloads,
)
from typing_extensions import (
    ParamSpec,
    TypeAliasType,
    TypeIs,
    TypeVar,
)

from jamjam._lib.typevars import K, P, R, T

_DP = ParamSpec("_DP", default=...)
_DV = TypeVar("_DV", default=object)
_DV_co = TypeVar("_DV_co", default=object, covariant=True)

Fn = Callable[_DP, _DV]  #:
Map = Mapping[K, _DV_co]  #:
Seq = Sequence[_DV_co]  #:
Module = ModuleType
"Default type of any module."
No = Never
"Alias of ``Never``."

Hint = type[object] | UnionType | TypeAliasType
"""Type of any (non-str) type-hint.

NOTE: isn't complete & may be impossible to do so.
"""

# Abbreviating these was *hard*. Iter = Iterator won as
# Iterator is the base concept (tho not base class) and the
# `iter` func really should return `Iter`.
Iter = Iterator[_DV_co]  #:
CanIter = Iterable[_DV_co]  #:

# EllipsisType is bad since it suggests type of `type(...)`
# but we can't use Ellipsis since that's a built-in alias
# for '...' itself.
Dots = EllipsisType
"Type of singleton/literal ``...``."

Two = tuple[_DV, _DV]
"Type of homogenous 2-tuple."
Three = tuple[_DV, _DV, _DV]
"Type of homogenous 3-tuple."
StrDict = dict[str, _DV]
"Type of a homogenous dictionary with string keys."
MethodDef = Fn[Concatenate[T, P], R]
"Parameterized type for method definitions."


class ParamsCopier(Protocol[P]):
    "A func which copies params for static checkers."

    def __call__(self, f: Fn[..., R], /) -> Fn[P, R]: ...


def copy_params(f: Fn[P, object], /) -> ParamsCopier[P]:
    """Transfer static signature of one func to another.

    NOTE: does not work with overloaded functions - might
    work with Callable protocol with overloaded ``__call__``?

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


def _match_overload(
    f: Fn, args: tuple[object, ...], kwds: StrDict
) -> tuple[Fn, tuple, StrDict[Any]]:
    # TODO: add runtime type-checking?

    for func_overload in get_overloads(f):
        s = signature(func_overload)
        try:
            bound = s.bind(*args, **kwds)
        except TypeError:
            continue
        # TODO: don't we need to call apply_defaults?
        # Add test case.
        return func_overload, bound.args, bound.kwargs
    name = f"{f.__module__}.{f.__qualname__}"
    msg = f"No overload of {name} for {args=}, {kwds=}."
    raise TypeError(msg)


def check_overloads(f: Fn[P, R], /) -> Fn[P, R]:
    "Check calls to ``f`` match an overload signatures."

    def new_func(*args: P.args, **kwds: P.kwargs) -> R:
        _, args, kwds = _match_overload(f, args, kwds)
        return f(*args, **kwds)

    update_wrapper(new_func, f)
    return new_func


def use_overloads(
    f: Fn[[], None] | MethodDef[No, [], None], /
) -> Fn:
    """Use ``@overload`` bodies to implement of ``f``.

    No (runtime) types checked, so signatures should not
    overlap even after stripping type hints.
    """

    def new_func(*args: object, **kwds: object) -> object:
        ofunc, args, kwds = _match_overload(f, args, kwds)
        return ofunc(*args, **kwds)

    update_wrapper(new_func, f)
    return new_func


def get_hints(v: Fn | type | Module) -> dict[str, Hint]:
    "Get a func/class/module's type-hints."
    return get_annotations(v, eval_str=True)


class _Delete:
    "Descriptor that deletes itself when it's assigned."

    def __set_name__(self, t: type, name: str) -> None:
        delattr(t, name)


def typing_only(_: MethodDef[T, P, R]) -> MethodDef[T, P, R]:
    "Decorate a method to make it unavailable at runtime."
    return _Delete()  # type: ignore[return-value]  # obvious lie


_no_hint: Any = object()


class HintWrap(Generic[T]):
    """Raise a type hints from annotations into runtime code.

    Through this class any hint can we manipulated at runtime
    inside of class methods, *without* requiring the loss of
    it's information to the type-checker.
    """

    # classvar, but can't use ClassVar[...] due to type var
    _hint: Hint = _no_hint

    @classmethod
    def get(cls) -> type[T]:
        hint = cls._hint
        if hint is _no_hint:
            msg = f"{cls.__name__} missing type-var value."
            raise TypeError(msg)
        # Not sure if this *should* be casted. Should become
        # obvious with more use cases.
        return cast(type[T], cls._hint)

    @abstractmethod
    def _dont_instantiate_(self) -> No: ...

    def __init_subclass__(
        cls, *, _hint: type[T] = _no_hint, **kwargs: object
    ) -> None:
        cls._hint = _hint
        return super().__init_subclass__(**kwargs)

    def __class_getitem__(cls, item: Any) -> type[Self]:
        if isinstance(item, tuple):
            msg = "Only one type parameter allowed."
            raise TypeError(msg)
        return type("HintAlias", (cls,), {}, _hint=item)


def _extended_isinstance(obj: object, hint: Hint) -> bool:
    if isinstance(hint, type):
        return isinstance(obj, hint)
    if isinstance(hint, UnionType):
        result = any(
            _extended_isinstance(obj, sub_hint)
            for sub_hint in get_args(hint)
        )
        return result

    origin = get_origin(hint)
    if origin is Literal:
        return obj in get_args(hint)
    if origin is Union:
        result = any(
            _extended_isinstance(obj, sub_hint)
            for sub_hint in get_args(hint)
        )
        return result

    msg = f"Type-hint {hint} is not supported."
    raise NotImplementedError(msg)


class Check(HintWrap[T]):
    "Generalized isinstance checks."

    # TODO: generalize this to include 3 modes: stingy,
    # generous and fail.
    @classmethod
    def has_instance(cls, obj: object) -> TypeIs[T]:
        "Check if ``obj`` is an instance of ``T``."
        return _extended_isinstance(obj, cls._hint)
