from textwrap import dedent

from jamjam._utils import unwrap


def test_format() -> None:
    txt = """
    Title: awesome.

    The focus of this meeting is that you suck.
    But I'm sure you can do better. Don't give up!

    Next on the agenda is pie. Pie is apparently delicious.
    Personally I'm not convinced. Though I usually won't
    say no to a pork pie.

    Bye bye!
    """

    expected = dedent("""\
    Title: awesome.

    The focus of this meeting is that you suck. But I'm sure you can do better. Don't give up!

    Next on the agenda is pie. Pie is apparently delicious. Personally I'm not convinced. Though I usually won't say no to a pork pie.

    Bye bye!""")

    assert unwrap(txt) == expected
