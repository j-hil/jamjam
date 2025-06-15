from __future__ import annotations

import sys
from ctypes import addressof, create_unicode_buffer
from enum import Enum
from warnings import warn
from winreg import (
    HKEY_CURRENT_USER,
    KEY_SET_VALUE,
    REG_DWORD,
    OpenKey,
    QueryValueEx,
    SetValueEx,
)

from jamjam._text import unwrap
from jamjam.classes import EzGetDesc
from jamjam.win import BROADCAST, Wm
from jamjam.winapi import user32


class _Mode(Enum):
    DARK = 0
    LIGHT = 1

    def __invert__(self) -> _Mode:
        return _Mode(not self.value)


class _Entry(EzGetDesc):
    R"An entry in the Themes\Personalize register."

    def __init__(self, name: str) -> None:
        self.name = name
        self._key = (
            HKEY_CURRENT_USER,
            R"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )

    def instance_get(self, _: object) -> _Mode:
        v, regtype = self._query()
        if v not in {0, 1}:
            msg = unwrap(f"""\
                Expected 0 or 1. Got {v} with {regtype=}. See
                https://docs.python.org/3/library/winreg.tml#value-types.
            """)
            raise RuntimeError(msg)
        return _Mode(v)

    def _query(self) -> tuple[object, int]:
        try:
            with OpenKey(*self._key) as key:
                return QueryValueEx(key, self.name)
        except FileNotFoundError:
            msg = f"WinReg entry {self.name!r} didn't exist."
            raise ValueError(msg) from None

    def __set__(self, _: object, mode: _Mode) -> None:
        # check entry exists; don't want new entries created
        self._query()
        value = mode.value
        with OpenKey(*self._key, access=KEY_SET_VALUE) as k:
            SetValueEx(k, self.name, 0, REG_DWORD, value)


class _Theme:
    app = _Entry("AppsUseLightTheme")
    sys = _Entry("SystemUsesLightTheme")

    @property
    def mode(self) -> _Mode:
        # app & sys theme *can* be out of sync. I only look
        # at app theme because visually it's more prominent.
        return self.app

    def set(self, mode: _Mode) -> None:
        self.app = mode
        self.sys = mode

    def swap(self) -> None:
        self.set(~self.mode)


def _update_mode(theme: _Theme, option: str) -> None:
    if option == "on":
        theme.set(_Mode.DARK)
        return
    if option == "swap":
        theme.swap()
        return
    if option == "off":
        theme.set(_Mode.LIGHT)
        return
    msg = f"Unrecognized option passed by user: {option}"
    raise RuntimeError(msg)


def _refresh_windows() -> None:
    "Send 'refresh' message to windows to pick up new mode."
    # Magic value sourced from:
    # https://github.com/sandboxie-plus/Sandboxie/issues/1270#issuecomment-940671165
    # TODO: would be nice if `winapi` did the conversion?
    param = create_unicode_buffer("ImmersiveColorSet")
    long = addressof(param)

    # Send this message to refresh explorer ...
    user32.SendMessageW(
        BROADCAST, Wm.SETTING_CHANGE, wParam=0, lParam=long
    )
    # ... then send this message to refresh task bar.
    user32.SendMessageW(
        BROADCAST, Wm.THEME_CHANGED, wParam=0, lParam=0
    )


def main() -> None:
    _, *options = sys.argv
    if not options:
        options = ["swap"]
    option, *extras = options
    if extras:
        msg = f"Ignoring extra options {extras}"
        warn(msg, stacklevel=2)

    theme = _Theme()
    before = theme.mode
    _update_mode(theme, option)
    _refresh_windows()
    after = theme.mode

    msg = unwrap(f"""
        Option {option!r} used. Theme was {before.name}
        and is now {after.name}.
    """)
    print(msg)


if __name__ == "__main__":
    main()
