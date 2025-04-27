"Access to the windows API."

# ruff: noqa: N802, N803, N815
from __future__ import annotations

import ctypes
from ctypes.wintypes import (
    DWORD,
    HWND,
    INT,
    LONG,
    LPCWSTR,
    SHORT,
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


class MouseInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-mouseinput/"

    dx: Long
    dy: Long
    mouseData: DWord | None = None
    dwFlags: DWord | None = None
    time: DWord | None = None
    dwExtraInfo: PULong | None = None


class KeybdInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput/"

    wVk: Word
    wScan: Word | None = None
    dwFlags: DWord | None = None
    time: DWord | None = None
    dwExtraInfo: PULong | None = None


class HardwareInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-hardwareinput/"

    uMsg: DWord
    wParamL: Word
    wParamH: Word


class Input(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-input/"

    class _U(c.Union): ...

    type: DWord
    mi: MouseInput = c.anonymous(_U)
    ki: KeybdInput = c.anonymous(_U)
    hi: HardwareInput = c.anonymous(_U)


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

    @imp_method
    def SendInput(
        self,
        cInputs: UInt,
        pInputs: c.Array[Input],
        cbSize: Int,
    ) -> UINT:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-sendinput/"
        raise NotImplementedError

    @imp_method
    def VkKeyScanW(self, ch: WChar) -> SHORT:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-vkkeyscanw/"
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
