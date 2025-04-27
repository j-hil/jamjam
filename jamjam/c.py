"Creation of type-safe accessors to C functions."
# ruff: noqa: SLF001

from __future__ import annotations

import _ctypes
import ctypes
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
    get_origin,
)

from jamjam.classes import mk_repr
from jamjam.typing import Hint, get_hints

_, _SimpleCData, _CData, _ = ctypes.c_int.mro()
_CArgObject = type(ctypes.byref(ctypes.c_int()))
_FuncPtr = ctypes.CFUNCTYPE(None).mro()[1]

if TYPE_CHECKING:
    BaseData = ctypes._CData
    Simple = ctypes._SimpleCData
    ArgObj = ctypes._CArgObject
    FuncPtr = _ctypes.CFuncPtr
    NamedFuncPtr = ctypes._NamedFuncPointer
else:
    BaseData = _CData
    Simple = _SimpleCData
    ArgObj = _CArgObject
    FuncPtr = _FuncPtr
    NamedFuncPtr = Any  # can only be used as a type-hint

_D = TypeVar("_D", bound=BaseData)
Array = ctypes.Array
"The array ctype."
Union = ctypes.Union
"The union ctype."


class _PointerHint(type):
    def __getitem__(cls, t: type[_D]) -> type[Pointer[_D]]:
        return ctypes.POINTER(t)

    def __call__(cls, data: _D) -> Pointer[_D]:
        return ctypes.pointer(data)

    def __instancecheck__(cls, instance: object) -> bool:
        return isinstance(instance, ctypes._Pointer)

    def __subclasscheck__(cls, subclass: type) -> bool:
        return issubclass(subclass, ctypes._Pointer)


if TYPE_CHECKING:
    Pointer = ctypes._Pointer
else:
    Pointer = _PointerHint("Pointer", (), {})

Int = int | ctypes.c_int
Str = str | ctypes.c_wchar_p


def extract(hint: Hint) -> type[Data]:
    "Extract the c-type from within a type-union."
    if isinstance(hint, UnionType):
        types = get_args(hint)
        return next(t for t in types if issubclass(t, Data))
    cls: type = get_origin(hint) or hint
    if issubclass(cls, Data):
        return cls
    msg = f"Expected union including a ctype. Got {hint=}"
    raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class Field:
    "Metadata for a ``c.Struct`` field."

    name: str
    hint: Hint
    ctype: type[Data]
    utype: type[Union] | None


if TYPE_CHECKING:
    _PyCStructType = _ctypes._PyCStructType
else:
    _PyCStructType = type(ctypes.Structure)


class _NewStructMeta(_PyCStructType, type):
    def _mk_field(cls, attr: str, hint: Hint) -> Field:
        ut = getattr(cls, attr, None)
        if ut is None or issubclass(ut, Union):
            return Field(attr, hint, extract(hint), ut)
        msg = (
            "Field must be unset, `None` or assigned"
            f"with `c.anonymous`. Instead got {ut}."
        )
        raise TypeError(msg)

    def __init__(cls, *args: object, **kwds: object) -> None:
        super().__init__(*args, **kwds)

        fields = {
            attr: cls._mk_field(attr, hint)
            for attr, hint in get_hints(cls).items()
        }
        groups = groupby(fields.values(), lambda f: f.utype)

        _anonymous_: list[str] = []
        ctype_fields: list[tuple[str, type[Data]]] = []
        for utype, group in groups:
            u_fields = [(f.name, f.ctype) for f in group]
            if utype is None:
                ctype_fields.extend(u_fields)
                continue
            utype._fields_ = u_fields
            uf = f"__anonymous_{utype.__name__}"
            ctype_fields.append((uf, utype))
            _anonymous_.append(uf)

        cls._anonymous_ = _anonymous_
        cls._fields_ = ctype_fields
        cls.__dataclass_fields__ = fields


# must return Any as assigned to typed fields
def anonymous(utype: type[Union]) -> Any:
    "Mark field as union member and anonymously accessible."
    return utype


@dataclass_transform(eq_default=False, kw_only_default=True)
class Struct(ctypes.Structure, metaclass=_NewStructMeta):
    "Create c-structs with dataclass like syntax"

    # TODO: anonymous union safety features?
    # 1. when calling init validate that 1 union arg set
    # 2. when accessing member check if it was one set in
    # init, otherwise error. else this can just be a system
    # error which is obtuse.

    @classmethod
    def size(cls) -> int:
        "Get size in bytes of a C object."
        return ctypes.sizeof(cls)

    def byref(self) -> ArgObj:
        "Get 'pointer' to C object usable only as a func arg"
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


Data = Simple | Pointer | FuncPtr | Union | Struct | Array
"""All BaseData subclasses.

Where relevant the ``jamjam.c`` class has replaced
the relevant ``ctypes`` class. This may be a mistake.
"""
