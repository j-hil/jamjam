"""Print some basic debug info."""

import datetime as dt
import sys


def _str_kwargs(**kwargs: object) -> list[str]:
    return [f"{kwd}: {arg}" for kwd, arg in kwargs.items()]


def main() -> None:
    msg = _str_kwargs(
        version=sys.version,
        interpeter=sys.exec_prefix,
        platform=sys.platform,
        time=dt.datetime.now(dt.UTC),
    )
    print(msg)


if __name__ == "__main__":
    main()
