"""Look busy!."""

from jamjam.win import Mb, user32


def main() -> None:
    user32.MessageBoxW(
        lpText="Hello there friend.",
        lpCaption="JamJam Idler",
        uType=Mb.OK_CANCEL | Mb.ICON_ERROR | Mb.ICON_INFO,
    )


if __name__ == "__main__":
    main()
