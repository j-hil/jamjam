def test_hash_clash() -> None:
    """Don't worry about hash clashes...

    ... so long as your `__eq__` is correct;
    i.e. that `a == b` => `hash(a) == hash(b)`.
    """

    class A:
        def __hash__(self) -> int:
            return 1

    class B:
        def __eq__(self, _: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 1

    class C:
        def __eq__(self, _: object) -> bool:
            return False

        def __hash__(self) -> int:
            return 1

    class D:
        def __eq__(self, _: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 2

    d = {
        A(): 1,  # entry 1
        A(): 2,  # entry 2
        B(): 3,  # entry 1
        B(): 4,  # entry 1
        C(): 5,  # entry 3
        C(): 6,  # entry 4
        D(): 7,  # entry 5
        D(): 8,  # entry 5
    }
    assert len(d) == 5
    assert [(type(k), v) for k, v in d.items()] == [
        (A, 4),  # entry 1
        (A, 2),  # entry 2
        (C, 5),  # entry 3
        (C, 6),  # entry 4
        (D, 8),  # entry 5
    ]
