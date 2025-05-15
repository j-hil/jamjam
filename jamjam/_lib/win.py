from __future__ import annotations

import ctypes
from functools import wraps
from inspect import signature
from typing import TypeVar, cast

from jamjam import c
from jamjam._lib.typevars import P
from jamjam.typing import MethodDef

D = TypeVar("D", bound=ctypes.CDLL)
R = TypeVar("R", bound=c.BaseData | c.PyNative)


def _errcheck(
    result: c.BaseData | c.PyNative,
    f: c.FuncPtr,
    args: tuple[c.BaseData, ...],
) -> c.Data:
    _ = args, f
    if errno := ctypes.get_last_error():
        raise ctypes.WinError(errno)
    if isinstance(result, c.PyNative):
        # Think stubs for `CFuncPtr.errcheck` don't capture
        # ctypes's special casing of PyNative hence cast.
        result = cast(c.Data, result)
    elif not isinstance(result, c.Data):
        msg = f"Expected c-type return. Got value {result}."
        raise TypeError(msg)
    return result


def imp_method(f: MethodDef[D, P, R]) -> MethodDef[D, P, R]:
    "Implement a WinDLL method from it's name & typing alone."
    method_name = f.__name__

    @wraps(f)
    def new_method_defn(
        self: D, /, *args: P.args, **kwargs: P.kwargs
    ) -> R:
        cfunc = self[method_name]
        method = getattr(self, method_name)
        sig = signature(method, eval_str=True)
        params = sig.parameters.values()
        argtypes = [c.extract(p.annotation) for p in params]

        cfunc.argtypes = argtypes
        cfunc.restype = c.extract(sig.return_annotation)
        cfunc.errcheck = _errcheck

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        missing = [
            param
            for param, arg in bound.arguments.items()
            if arg is c.REQUIRED
        ]
        if missing:
            msg = f"Required param(s) {missing} missing."
            raise TypeError(msg)
        return cfunc(*bound.arguments.values())

    return new_method_defn
