from textwrap import dedent

from jamjam.jank import capture, identify, textify


def test_textify() -> None:
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


def test_identify() -> None:
    assert identify(1 + 2) == ("1 + 2", 3)

    x0 = object()
    name, x1 = identify(x0)
    assert name == "x0"
    assert x1 is x0


def test_capture() -> None:
    with capture() as text:
        x = 100
        y = 300
        _ = x, y

    expected = dedent("""
        x = 100
        y = 300
        _ = x, y
    """).strip()
    assert text == expected
