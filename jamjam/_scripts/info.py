"""Print some basic debug info."""

import datetime as dt
import sys


def _lines(**kwargs: object) -> list[str]:
    return [f"{kwd}: {arg}" for kwd, arg in kwargs.items()]


def main() -> None:
    lines = _lines(
        version=sys.version,
        interpeter=sys.exec_prefix,
        platform=sys.platform,
        time=dt.datetime.now(dt.UTC),
    )
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
