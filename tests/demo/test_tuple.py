from timeit import timeit


def test_construction_speed() -> None:
    """Never use += operator..."""
    loop1 = 100
    loop2 = 1000

    def append_list_then_convert() -> None:
        array = []
        for i in range(loop1):
            array.append(i)  # noqa: PERF402
        array = tuple(array)

    def add_tuple() -> None:
        array = tuple[int, ...]()
        for i in range(loop1):
            array += (i,)

    def unpack_repack() -> None:
        array = tuple[int, ...]()
        for i in range(loop1):
            array = (*array, i)

    t1 = timeit(append_list_then_convert, number=loop2)
    t2 = timeit(add_tuple, number=loop2)
    t3 = timeit(add_tuple, number=loop2)

    # not even close
    assert t2 / t1 > 4
    assert t3 / t1 > 4
