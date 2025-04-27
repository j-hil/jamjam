from jamjam.iter import ii, split


def test_split() -> None:
    odd, even = split(range(10), lambda x: x % 2)
    assert list(odd) == [1, 3, 5, 7, 9]
    assert list(even) == [0, 2, 4, 6, 8]

    truthy, falsy = split([0, 1, False, True, "", " "])
    assert list(truthy) == [1, True, " "]
    assert list(falsy) == [0, False, ""]


def test_ii() -> None:
    r1 = ii(4, 8, ..., 20)
    assert isinstance(r1, range)
    assert list(r1) == [8, 12, 16]

    r2 = ii(4, ..., 8)
    assert list(r2) == [5, 6, 7]

    r3 = ii[4, 8, ..., 20]
    assert list(r3) == [4, 8, 12, 16, 20]

    r4 = ii[4, ..., 8]
    assert list(r4) == [4, 5, 6, 7, 8]
