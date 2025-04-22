"Access to the windows API."

# ruff: noqa: N802, N803
from __future__ import annotations

import ctypes
from ctypes.wintypes import (
    DWORD,
    HWND,
    INT,
    LONG,
    LPCWSTR,
    UINT,
    ULONG,
    WCHAR,
    WORD,
)
from enum import IntEnum

from jamjam import c
from jamjam._lib.win import REQUIRED, imp_method

Hwnd = int | HWND
LpCwStr = str | LPCWSTR
UInt = int | UINT
Int = int | INT
Long = int | LONG
DWord = int | DWORD
Word = int | WORD
PULong = c.Pointer[ULONG]
WChar = str | WCHAR


class User32(ctypes.WinDLL):
    "Type of ``user32``."

    def __init__(self) -> None:
        super().__init__("user32")

    @imp_method
    def MessageBoxW(
        self,
        hWnd: Hwnd | None = None,
        lpText: LpCwStr | None = None,
        lpCaption: LpCwStr | None = None,
        uType: UInt = REQUIRED,
    ) -> INT:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-messageboxw/"
        raise NotImplementedError


user32 = User32()
"https://learn.microsoft.com/en-gb/windows/win32/api/winuser/"


class Mb(IntEnum):
    "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-messageboxw#parameters/"

    OK = 0x00
    OK_CANCEL = 0x01
    ABORT_RETRY_IGNORE = 0x02
    YN_CANCEL = 0x03
    YN = 0x04
    RETRY_CANCEL = 0x05
    CANCEL_TRY_CONT = 0x06

    ICON_ERROR = 0x10
    ICON_QUESTION = 0x20
    ICON_WARNING = 0x30
    ICON_INFO = 0x40


if __name__ == "__main__":
    user32.MessageBoxW(
        lpCaption="My Test",
        lpText="Hello! welcome to my first text box.",
        uType=Mb.OK_CANCEL | Mb.ICON_INFO,
    )
