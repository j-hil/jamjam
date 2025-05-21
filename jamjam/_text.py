"Text formatting."

from io import StringIO
from textwrap import dedent


def unwrap(txt: str) -> str:
    "Remove indent, trailing whitespace & line wrapping."
    lines = iter(dedent(txt.strip()).splitlines())

    prev = next(lines, "")
    stream = StringIO()
    stream.write(prev)
    for line in lines:
        line = line.strip()
        if line:
            stream.write(" " if prev else "\n\n")
            stream.write(line)
        prev = line

    return stream.getvalue()
