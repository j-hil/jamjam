"""Creation of type-safe accessors to C functions.

Could be made redundant in future:
https://github.com/python/cpython/issues/104533
"""
# ruff: noqa: SLF001

from __future__ import annotations

import _ctypes
import ctypes
from dataclasses import dataclass
from itertools import groupby
from textwrap import indent
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Self,
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


Array = ctypes.Array
"The array ctype."
Union = ctypes.Union
"The union ctype."
PyNative = int | bytes | str | None
"Python native types `ctypes` auto wraps/unwraps."
REQUIRED: Any = object()
"Default for required params located after optional ones."
OPTIONAL: Any = object()
"Default for optional params."

# Cannot expand _D to include (annotated) PyNative as
# ctypes._Pointer is generic only in BaseData.
_D = TypeVar("_D", bound=BaseData)


class _PointerHint(type):
    def __getitem__(cls, t: type[_D]) -> type[Pointer[_D]]:
        try:
            return ctypes.POINTER(t)
        except TypeError:
            # eg `t` is valid as a type-var but not a single
            # class so return generic pointer class.
            return ctypes._Pointer

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

Int = Annotated[int, ctypes.c_int]
Str = Annotated[str, ctypes.c_wchar_p]


def extract(hint: Hint) -> type[Data]:
    "Extract the c-type from an annotated type."
    origin = get_origin(hint)
    cls = origin or hint
    if isinstance(cls, type) and issubclass(cls, Data):
        return cls
    if origin is Annotated:
        _, *metadata = get_args(hint)
        for t in metadata:
            if isinstance(t, type) and issubclass(t, Data):
                return t
    msg = f"Expected ctype or annotated py-type. Got {hint=}"
    raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class Field:
    "Metadata for a ``c.Struct`` field."

    name: str
    hint: Hint
    ctype: type[Data]
    optional: bool
    utype: type[Union] | None


if TYPE_CHECKING:
    _PyCStructType = _ctypes._PyCStructType
else:
    _PyCStructType = type(ctypes.Structure)


class _NewStructMeta(_PyCStructType, type):
    def _mk_field(cls, attr: str, hint: Hint) -> Field:
        unset = object()
        v = getattr(cls, attr, unset)
        if v is unset:
            ut = None
            optional = False
        elif v is OPTIONAL:
            ut = None
            optional = True
        elif isinstance(v, type) and issubclass(v, Union):
            ut = v
            optional = True
        else:
            msg = (
                "Field must be unset or assigned with "
                f"`OPTIONAL` or `c.anonymous`; not {v}."
            )
            raise TypeError(msg)
        return Field(attr, hint, extract(hint), optional, ut)

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
    # 3. Allow positional args?

    @classmethod
    def size(cls) -> int:
        "Get size in bytes of a C object."
        return ctypes.sizeof(cls)

    def byref(self) -> Pointer[Self]:
        "Get 'pointer' to C obj usable only as a func arg."
        # Lie here as not sure how to fit real return of
        # ArgObj into DLL signatures easily.
        return ctypes.byref(self)  # type: ignore[return-value]

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
