from collections.abc import Callable
from typing_extensions import ParamSpec, TypeVar

K = TypeVar("K")
R = TypeVar("R")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_con = TypeVar("T_con", contravariant=True)
V_co = TypeVar("V_co", covariant=True)

F = TypeVar("F", bound=Callable)

P = ParamSpec("P")
