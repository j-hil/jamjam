"These don't yet have a home."

from io import StringIO
from textwrap import dedent
from typing import Never


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


Ex = BaseException


def raise_(ex: Ex | type[Ex] = AssertionError) -> Never:
    raise ex
