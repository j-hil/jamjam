import functools
import inspect
from collections.abc import Callable, Mapping
from typing import ParamSpec, TypeVar, get_overloads

P = ParamSpec("P")
R = TypeVar("R")


class OverloadError(TypeError):
    def __init__(
        self,
        func: Callable[..., object],
        args: tuple[object, ...],
        kwargs: Mapping[str, object],
    ) -> None:
        msg = f"No matching overload for {func.__qualname__} with {args=}, {kwargs=}."
        super().__init__(msg)


def check_overloads(func: Callable[P, R], /) -> Callable[P, R]:
    """Check calls made match one of the overloads.

    Does not check types.
    """
    # TODO: add runtime type-checking?

    def new_func(*args: P.args, **kwargs: P.kwargs) -> R:
        for func_overload in get_overloads(func):
            signature = inspect.signature(func_overload)
            try:
                bound_args = signature.bind(*args, **kwargs)
            except TypeError:
                continue
            return func(*bound_args.args, **bound_args.kwargs)
        raise OverloadError(func, args, kwargs)

    functools.update_wrapper(new_func, func)
    return new_func


def use_overloads(func: Callable[[], None], /) -> Callable[..., object]:
    """Use the body of an overload as the implementation of a function.

    Does not check types so signatures should not overlap when typing is stripped.
    """
    # TODO: add runtime type-checking?

    def new_func(*args: object, **kwargs: object) -> object:
        for func_overload in get_overloads(func):
            signature = inspect.signature(func_overload)
            try:
                bound_args = signature.bind(*args, **kwargs)
            except TypeError:
                continue
            return func_overload(*bound_args.args, **bound_args.kwargs)
        raise OverloadError(func, args, kwargs)

    functools.update_wrapper(new_func, func)
    return new_func
