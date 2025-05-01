from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any

_log = logging.getLogger(__name__)


def test_metaclass() -> None:
    """Demo how metaclass instantiation works.

    Steps adapted python `data-modal`_:

    1. MRO entries are resolved
    2. appropriate metaclass is determined
    3. class namespace is prepared
    4. class body executed, populating 'prepared' namespace
    5. class object is created

    .. _data-modal: https://docs.python.org/3/reference/datamodel.html#metaclasses
    """

    class Namespace(dict[str, object]):  # noqa: FURB189
        def __setitem__(
            self, key: str, value: object
        ) -> None:
            _log.info(f"Set item {key} to value {value}")
            super().__setitem__(key, value)

    class Meta(type):
        @classmethod
        def __prepare__(
            cls,
            name: str,
            bases: tuple[type, ...],
            /,
            **kwargs: object,
        ) -> MutableMapping[str, object]:
            namespace = super().__prepare__(
                name, bases, **kwargs
            )
            namespace = Namespace(namespace)
            namespace["prepared"] = True

            _log.info(f"3. Namespace of {name} is prepared.")
            return namespace

        def __new__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            /,
            **kwds: Any,
        ) -> Meta:
            class_name = "C"
            test_name = test_metaclass.__name__
            qual_name = f"{test_name}.<locals>.{class_name}"
            if name == class_name:
                assert bases == (A, B)
                assert namespace == {
                    "__module__": __name__,
                    # surprisingly useful to know about:
                    "__qualname__": qual_name,
                    "member": 101,
                    "prepared": True,
                }
                # meta-classes should remove used kwds, then
                # pass remaining; same as `__init_subclass__`
                assert kwds.pop("kwd1") == 1
                assert kwds.pop("kwd2") == "foo"
                _log.info(f"5. New class {name} created")

            v = super().__new__(
                cls, name, bases, namespace, **kwds
            )
            return v

    class A: ...

    class B: ...

    class C(A, B, metaclass=Meta, kwd1=1, kwd2="foo"):
        # this block is executed and then it's namespace
        # passed to `Meta.__new__` via the mapping returned
        # by `Meta.__prepare__`
        member = 1 + 100
        _log.info(f"4. Inside {__qualname__} body.")

    assert type(C) is Meta
    assert type(C) is not type
    assert isinstance(C, type)
