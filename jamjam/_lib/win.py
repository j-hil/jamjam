from __future__ import annotations

import ctypes
from functools import wraps
from inspect import signature
from typing import Generic, ParamSpec, TypeVar, cast

from jamjam import c
from jamjam.classes import EzGetDesc
from jamjam.typing import Fn, MethodDef

P = ParamSpec("P")
T = TypeVar("T")
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
    "Implement a WinDLL method from it's name & typing."
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


def _win_cfuncify(f: Fn) -> c.FuncPtr:
    sig = signature(f, eval_str=True)
    params = list(sig.parameters.values())

    argtypes = [c.extract(p.annotation) for p in params]
    rtype = c.extract(sig.return_annotation)
    return ctypes.WINFUNCTYPE(rtype, *argtypes)(f)


class WinFuncDesc(EzGetDesc[c.FuncPtr, T], Generic[T, P, R]):
    def __init__(self, f: MethodDef[T, P, R]) -> None:
        self.method_def = f
        # Apparently necessary to stash cfuncs to prevent gc
        # removing them. Prevents nasty bugs. See:
        # https://stackoverflow.com/questions/7901890
        self.cfuncs: dict[T, c.FuncPtr] = {}

    def instance_get(self, x: T) -> c.FuncPtr:
        cfunc = self.cfuncs.get(x)
        if cfunc is None:
            method = self.method_def.__get__(x)
            cfunc = self.cfuncs[x] = _win_cfuncify(method)
        return cfunc
