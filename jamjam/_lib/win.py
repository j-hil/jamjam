from __future__ import annotations

import ctypes
from functools import wraps
from inspect import signature
from types import UnionType
from typing import Any, TypeVar, get_args

from jamjam import c
from jamjam._lib.typevars import P, R
from jamjam.typing import MethodDef, Seq

D = TypeVar("D", bound=ctypes.CDLL)
REQUIRED: Any = object()
"Default for required params located after optional ones."


def _extract(hint: UnionType | type[c.Data]) -> type[c.Data]:
    if isinstance(hint, UnionType):
        types = get_args(hint)
        return next(
            t for t in types if issubclass(t, c.Data)
        )
    if issubclass(hint, c.BaseData):
        return hint
    msg = (
        "Expected a type-hint of to be either a c-type "
        f"or a union including a c-type. Got {hint=}."
    )
    raise TypeError(msg)


def _errcheck(
    result: object, f: c.FuncPtr, args: Seq[c.BaseData]
) -> c.Data:
    _ = args
    rt = f.restype
    if not (isinstance(rt, type) and issubclass(rt, c.Data)):
        msg = f"Expected c-type return. Got {rt} from {f}."
        raise TypeError(msg)
    if not result:
        raise ctypes.WinError()
    if not isinstance(result, c.Data):
        if not issubclass(rt, c.SimpleData):
            msg = f"Can't coerce {result} into ctype {rt}."
            raise TypeError(msg)
        result = rt(result)
    return result


def imp_method(f: MethodDef[D, P, R]) -> MethodDef[D, P, R]:
    "Implement a CDLL method from it's name & typing alone."
    method_name = f.__name__

    @wraps(f)
    def new_method_defn(
        self: D, /, *args: P.args, **kwargs: P.kwargs
    ) -> R:
        cfunc = self[method_name]
        method = getattr(self, method_name)
        sig = signature(method, eval_str=True)
        params = sig.parameters.values()
        argtypes = [_extract(p.annotation) for p in params]

        cfunc.argtypes = argtypes
        cfunc.restype = sig.return_annotation
        cfunc.errcheck = _errcheck

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        missing = [
            param
            for param, arg in bound.arguments.items()
            if arg is REQUIRED
        ]
        if missing:
            msg = f"Required param(s) {missing} missing."
            raise TypeError(msg)
        return cfunc(*bound.arguments.values())

    return new_method_defn
