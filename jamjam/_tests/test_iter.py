from jamjam.iter import split


def test_split() -> None:
    odd, even = split(range(10), lambda x: x % 2)
    assert list(odd) == [1, 3, 5, 7, 9]
    assert list(even) == [0, 2, 4, 6, 8]

    truthy, falsy = split([0, 1, False, True, "", " "])
    assert list(truthy) == [1, True, " "]
    assert list(falsy) == [0, False, ""]
