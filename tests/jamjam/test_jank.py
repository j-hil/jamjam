from jamjam.jank import textify


def test_symtext() -> None:
    assert textify(int | str) == "int | str"

    # multi-line
    actual = textify(
        1 + 2,
        3 + 4,
        5 + 6,
    )  # fmt: skip
    expected = """
        1 + 2,
        3 + 4,
        5 + 6,
    """
    assert actual == expected

    # renamed func
    f = textify
    assert f("hello", there=1) == '"hello", there=1'
