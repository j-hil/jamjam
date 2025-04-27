from typing import Self


def test_new_then_init() -> None:
    class A:
        constructed = False
        initialized = False

        def __new__(cls) -> Self:
            self = super().__new__(cls)
            self.constructed = True
            return self

        def __init__(self) -> None:
            self.initialized = True

    a1 = A()
    assert a1.constructed
    assert a1.initialized

    a2 = A.__new__(A)
    assert a2.constructed
    assert not a2.initialized


def test_manual_init_in_new() -> None:
    class B:
        constructed = 0
        initialized = 0

        def __new__(cls) -> Self:
            self = super().__new__(cls)
            self.constructed += 1
            self.__init__()
            return self

        def __init__(self) -> None:
            self.initialized += 1

    b = B()
    assert b.constructed == 1
    assert b.initialized == 2
