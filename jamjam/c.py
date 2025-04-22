"Creation of type-safe accessors to C functions."
# ruff: noqa: SLF001

from __future__ import annotations

import _ctypes
import ctypes
from ctypes import CFUNCTYPE
from typing import TYPE_CHECKING, Any, TypeVar

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
