"""Easy-Enum.

A dataclass-like experience for enums, born out of the pain from Enum Subclass Hell.
Built-in enum should still be preferred where possible especially in simple cases;
it is more fully featured and better supported by the type-checkers.

Pros:
  * can subclass types with other meta-classes easily
  * less need for intermediary classes (eg `@dataclass` can be applied directly)
  * less magic (relatively) so easier to debug & declare as intended
  * easier creation of normal (non-enum) attributes that work with type-checkers

Cons:
  * Doesn't support `Literal[MyEnum.A]` for type-checkers
  * More verbose for simple cases

TODO: allow use of custom new - _new_new_?
TODO: add _post_class_init_?
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterator
from inspect import getmembers_static
from typing import (
    Any,
    ClassVar,
    Protocol,
    Self,
    TypeVar,
    cast,
    final,
)

from jamjam.classes import Singleton
from jamjam.typing import Hint


class EnumI(Protocol):
    # This is the only *required* method for subclasses.
    # Not a static method so you can implement in a parent class before enum-type.
    @classmethod
    @abstractmethod
    def _create_next_(
        cls, i: int, name: str, prev: tuple[Self, ...], /
    ) -> Self:
        raise NotImplementedError


EnumType = type[EnumI]
_EnumT = TypeVar("_EnumT", bound=EnumI)
_PMT = TypeVar("_PMT", bound="_ProtoMember")
_T = TypeVar("_T")
_Repr = Callable[[_T], str]


class _Missing(Singleton): ...


class _ProtoMember:
    """Transient descriptor used in enum creation.

    Each subclass is co-operatively implemented by itself, `Auto` & `enum`.
    The principle is:
      * `Auto` manages public instantiation (to mask the typing) always via `make`
      * `enum` handles replacement & cleanup, conditioning on type(...)
      * the proto member itself handles the rest
    """

    # finalized since used by make method
    @final
    def __init__(self, hint: Any) -> None:
        self.auto_hint = hint

    def __set_name__(
        self, owner: EnumType, name: str
    ) -> None:
        self.owner = owner
        self.name = name
        self.super_attr = getattr(
            super(owner, owner), name, _Missing()
        )

    def __get__(
        self, obj: EnumI | None, owner: EnumType
    ) -> object:
        if obj is None:
            if _Missing.is_(self.super_attr):
                msg = f"No attribute {self.name}."
                raise AttributeError(msg)
            return self.super_attr
        return getattr(super(owner, obj), self.name)

    @classmethod
    def make(
        cls, hint: Any
    ) -> Any:  # return Any to reduce littering type-ignores.
        return cls(hint)

    def __repr__(self) -> str:
        owner = self.owner.__qualname__
        cls = self.__class__.__qualname__
        return f"{cls}({owner}.{self.name})"


class _ProtoEnumeral(_ProtoMember):
    lookup_count: ClassVar = dict[EnumType, int]()
    """Tracks number of proto members for each enum so far.

    `@enum` removes the entry of the class it wraps, so shouldn't leak,
    and should usually be length 0 or 1.
    """
    # TODO: add test for this ^

    def __set_name__(
        self, owner: EnumType, name: str
    ) -> None:
        super().__set_name__(owner, name)

        count = self.lookup_count.get(owner, -1) + 1
        self.index = self.lookup_count[owner] = count

        enum_name = self.owner.__name__
        if self.auto_hint not in [Self, enum_name]:
            msg = (
                f"Type-param of {Auto.__name__} must be `Self` or `{enum_name!r}`."
                f"Got {self.auto_hint} instead."
            )
            raise TypeError(msg)


class _ProtoIter(_ProtoMember): ...


class _ProtoRepr(_ProtoMember): ...


class Auto(Hint[_EnumT]):
    """Use class methods of `Auto[Self]` to define enumeral members."""

    @classmethod
    def __make(cls, type_proto: type[_PMT]) -> Any:
        return type_proto(cls.get_hint())

    @classmethod
    def enumeral(cls) -> _EnumT:
        return cls.__make(_ProtoEnumeral)

    @classmethod
    def enumeral_list(
        cls, count: int, /
    ) -> Iterator[_EnumT]:
        return (cls.enumeral() for _ in range(count))

    @classmethod
    def enumeral_batch(
        cls, arg0: int, *args: int
    ) -> Iterator[Iterator[_EnumT]]:
        return (cls.enumeral_list(n) for n in (arg0, *args))

    @classmethod
    def enumeral_table(
        cls, rows: int, cols: int
    ) -> Iterator[Iterator[_EnumT]]:
        args = (cols for _ in range(rows))
        return cls.enumeral_batch(*args)

    @classmethod
    def give_class_iter(
        cls,
    ) -> classmethod[_EnumT, [], Iterator[_EnumT]]:
        return cls.__make(_ProtoIter)

    @classmethod
    def give_repr(cls) -> _Repr[object]:
        return cls.__make(_ProtoRepr)


class _LookupProtoMembers(
    dict[type[_ProtoMember], list[_ProtoMember]]
):
    def __getitem__(self, k: type[_PMT]) -> list[_PMT]:
        return cast(list[_PMT], self.setdefault(k, []))

    def take(self, k: type[_PMT]) -> list[_PMT]:
        return cast(list[_PMT], self.pop(k, []))


# we don't inherit from `EnumI` or `ABC` so that meta-classes are supported
class EnumMixin:
    """Optionally inherit provide *all* available standard enum stuff."""

    @classmethod
    @abstractmethod
    def _create_next_(
        cls, i: int, name: str, prev: tuple[Self, ...], /
    ) -> Self:
        raise NotImplementedError

    iter = Auto[Self].give_class_iter()
    __repr__ = Auto[Self].give_repr()


def enum(enum_cls: type[_EnumT], /) -> type[_EnumT]:
    # TODO: probably not going to play nice with slots

    original__hash__ = enum_cls.__hash__
    original__eq__ = enum_cls.__eq__
    original__init__ = enum_cls.__init__
    original__new__ = enum_cls.__new__
    original__repr__ = enum_cls.__repr__

    def __hash__(self: _EnumT) -> int:
        try:
            return original__hash__(self)
        except TypeError:
            return object.__hash__(self)

    def __eq__(self: _EnumT, other: object) -> bool:
        return self is other or original__eq__(self, other)

    for f in [__hash__, __eq__]:
        setattr(enum_cls, f.__name__, f)

    auto_hints = list[Any]()
    proto_members = _LookupProtoMembers()

    for _, v in getmembers_static(enum_cls):
        if isinstance(v, _ProtoMember):
            proto_members[type(v)].append(v)
            auto_hints.append(v.auto_hint)

    enumerals = dict[_EnumT, _ProtoEnumeral]()
    for v in proto_members.take(_ProtoEnumeral):
        enumeral = enum_cls._create_next_(
            v.index, v.name, tuple(enumerals)
        )
        setattr(enum_cls, v.name, enumeral)
        enumerals[enumeral] = v

    if not enumerals:
        msg = "Found no enum-member symbols. Use: `A = Auto[Self].enumeral()` etc."
        raise TypeError(msg)

    for v in proto_members.take(_ProtoIter):

        def iter(cls: type[_EnumT]) -> Iterator[_EnumT]:
            yield from enumerals

        setattr(enum_cls, v.name, classmethod(iter))

    for v in proto_members.take(_ProtoRepr):

        def __repr__(self: _EnumT) -> str:
            cls = self.__class__
            if self in enumerals:
                return f"<{cls.__qualname__}.{enumerals[self].name}>"
            # this *can* occur, eg during error handling
            return original__repr__(self)

        setattr(enum_cls, v.name, __repr__)

    if proto_members:
        msg = f"Found unhandled proto-members of types {list(proto_members)}."
        raise AssertionError(msg)

    marked_final = getattr(enum_cls, "__final__", False)
    if Self in auto_hints and not marked_final:
        # sadly can't mark it for people; type-checkers won't see it
        enum_name = enum_cls.__name__
        msg = (
            f"If using `{Auto.__name__}[Self]` you must mark {enum_name} with `@final`."
            f"Alternatively use `{Auto.__name__}['{enum_name}'] instead."
        )
        raise TypeError(msg)

    @staticmethod  # type: ignore[misc]
    def __new__(
        cls: type[_EnumT], *args: Any, **kwargs: Any
    ) -> _EnumT:
        try:
            self = original__new__(cls, *args, **kwargs)
        except TypeError:
            self = original__new__(cls)
        original__init__(self, *args, **kwargs)

        proto_enumeral = enumerals.get(self)
        if proto_enumeral is None:
            msg = f"Cannot make new instance {self} of enum {cls.__qualname__}."
            raise TypeError(msg)
        return getattr(cls, proto_enumeral.name)

    def __init__(
        self: _EnumT, *args: object, **kwargs: object
    ) -> None:
        # no op, since we now manually call the old init in __new__
        _ = self, args, kwargs

    @classmethod  # type: ignore[misc]
    def __init_subclass__(cls: type, /, **_: object) -> None:
        msg = f"Cannot subclass enum-type `{cls.__qualname__}`."
        raise TypeError(msg)

    for f in [__new__, __init__, __init_subclass__]:
        setattr(enum_cls, f.__name__, f)

    del _ProtoEnumeral.lookup_count[enum_cls]
    return enum_cls
