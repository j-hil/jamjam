"Creation of type-safe accessors to C functions."
# ruff: noqa: SLF001

from __future__ import annotations

import _ctypes
import ctypes
from ctypes import CFUNCTYPE, Union
from dataclasses import dataclass
from itertools import groupby
from textwrap import indent
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    dataclass_transform,
    get_args,
)

from jamjam.classes import mk_repr, mk_subtype
from jamjam.typing import get_hints

_, _SimpleCData, _CData, _ = ctypes.c_int.mro()
_CArgObject = type(ctypes.byref(ctypes.c_int()))
_FuncPtr = CFUNCTYPE(None).mro()[1]

if TYPE_CHECKING:
    BaseData = ctypes._CData
    SimpleData = ctypes._SimpleCData
    ArgObj = ctypes._CArgObject
    FuncPtr = _ctypes.CFuncPtr
    NamedFuncPtr = ctypes._NamedFuncPointer
else:
    BaseData = _CData
    SimpleData = _SimpleCData
    ArgObj = _CArgObject
    FuncPtr = _FuncPtr
    NamedFuncPtr = Any  # can only be used as a type-hint

_D = TypeVar("_D", bound=BaseData)
_Pointer = ctypes._Pointer


class _PointerHint(type):
    def __getitem__(cls, t: type[_D]) -> type[Pointer[_D]]:
        return ctypes.POINTER(t)

    def __call__(cls, data: _D) -> Pointer[_D]:
        return ctypes.pointer(data)

    def __instancecheck__(cls, instance: object) -> bool:
        return isinstance(instance, _Pointer)

    def __subclasscheck__(cls, subclass: type) -> bool:
        return issubclass(subclass, _Pointer)


if TYPE_CHECKING:
    Pointer = ctypes._Pointer
else:
    Pointer = _PointerHint("Pointer", (), {})
Data = (
    SimpleData
    | Pointer
    | FuncPtr
    | ctypes.Union
    | ctypes.Structure
    | ctypes.Array
)
"All basic BaseData subclasses."
Int = int | ctypes.c_int
Str = str | ctypes.c_wchar_p


def extract(hint: UnionType | type[Data]) -> type[Data]:
    "Extract the c-type from within a type-union."
    if isinstance(hint, UnionType):
        types = get_args(hint)
        return next(t for t in types if issubclass(t, Data))
    if issubclass(hint, BaseData):
        return hint
    msg = f"Expected union including a ctype. Got {hint=}"
    raise TypeError(msg)


# TODO: c.Union stuff still tentative - need use/test
class _UnionId(int): ...


@dataclass(frozen=True, slots=True)
class Field:
    "Metadata for a ``c.Struct`` field."

    name: str
    hint: type[object]
    ctype: type[Data]
    uid: _UnionId | None


if TYPE_CHECKING:
    _PyCStructType = _ctypes._PyCStructType
else:
    _PyCStructType = type(ctypes.Structure)


class _NewStructMeta(_PyCStructType, type):
    # TODO: types here
    def _mk_field(cls, attr: str, hint: Any) -> Field:
        uid = getattr(cls, attr, None)
        if not isinstance(uid, _UnionId | None):
            msg = (
                "Field must be unset, `None` or assigned"
                f"a union-id. Instead got {uid}."
            )
            raise TypeError(msg)
        return Field(attr, hint, extract(hint), uid)

    def __init__(cls, *args: object, **kwds: object) -> None:
        super().__init__(*args, **kwds)

        dc_fields = {
            attr: cls._mk_field(attr, hint)
            for attr, hint in get_hints(cls).items()
        }
        groups = groupby(dc_fields.values(), lambda f: f.uid)

        anonymous: list[str] = []
        ctype_fields: list[tuple[str, type[Data]]] = []
        for uid, group in groups:
            u_fields = [(f.name, f.ctype) for f in group]
            if uid is None:
                ctype_fields.extend(u_fields)
                continue
            ut = mk_subtype(f"__GeneratedUnion{uid}", Union)
            ut._fields_ = u_fields
            uf = f"__generated_field{uid}"
            ctype_fields.append((uf, ut))
            anonymous.append(uf)

        cls._anonymous_ = anonymous
        cls._fields_ = ctype_fields
        cls.__dataclass_fields__ = dc_fields


@dataclass_transform(eq_default=False)
class Struct(ctypes.Structure, metaclass=_NewStructMeta):
    "Create c-structs with dataclass like syntax"

    @classmethod
    def size(cls) -> int:
        return ctypes.sizeof(cls)

    def byref(self) -> ArgObj:
        return ctypes.byref(self)

    def __repr__(self) -> str:
        fields = {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }
        return mk_repr(self, fields)

    def __str__(self) -> str:
        cls_name = self.__class__.__qualname__

        parts = list[str]()
        for field in self.__dataclass_fields__:
            v = getattr(self, field)
            if isinstance(v, Struct):
                v = str(v)
            elif isinstance(v, Data):
                v = f"<{v.__class__.__name__} @ {id(v):X}>"
            else:
                v = repr(v)
            part = f"{field}={v},"
            part = indent(part, prefix=" " * 4)
            parts.append(part)

        body = "\n".join(parts)
        return f"{cls_name}(\n{body}\n)"
