def test_assignment() -> None:
    class A:
        def f(self) -> int:
            return 1

    assert A().f() == 1
    assert A.f(A()) == 1

    def g(self: A) -> int:
        _ = self
        return 2

    A.f = g  # type: ignore[method-assign]
    assert A().f() == 2
    assert A.f(A()) == 2


def test_name() -> None:
    class A:
        def f(self) -> None: ...

        x = f

    # so FunctionType descriptor doesn't replace defn name with member name
    # (which could be done via __set_name__)
    assert A.x.__name__ == A.f.__name__
