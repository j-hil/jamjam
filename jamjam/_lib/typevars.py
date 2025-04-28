from collections.abc import Callable
from typing_extensions import ParamSpec, TypeVar

# NOTE: would use infer_variance but can't due to
# https://github.com/python/mypy/issues/17811
K = TypeVar("K")
R = TypeVar("R")
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_con = TypeVar("T_con", contravariant=True)
V_co = TypeVar("V_co", covariant=True)

X = TypeVar("X", contravariant=True)
"Contravariant & un-defaulted."

F = TypeVar("F", bound=Callable[..., object])

P = ParamSpec("P")
