"""Access to the windows API.

This module is intentionally written in a way to make it
easy to auto-generate, should I ever need to.
More 'bespoke' wrappers are in ``jamjam.win``.
"""

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
from enum import IntEnum, IntFlag

from jamjam import c
from jamjam._lib.win import REQUIRED, imp_method
from jamjam.classes import autos
from jamjam.iter import irange

Hwnd = int | HWND  #:
LpCwStr = str | LPCWSTR  #:
UInt = int | UINT  #:
Int = int | INT  #:
Long = int | LONG  #:
DWord = int | DWORD  #:
Word = int | WORD  #:
PULong = c.Pointer[ULONG]  #:
WChar = str | WCHAR  #:


class MouseInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-mouseinput/"

    dx: Long  #:
    dy: Long  #:
    mouseData: DWord | None = None  #:
    dwFlags: DWord | None = None  #:
    time: DWord | None = None  #:
    dwExtraInfo: PULong | None = None  #:


class KeybdInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput/"

    wVk: Word  #:
    wScan: Word | None = None  #:
    dwFlags: DWord | None = None  #:
    time: DWord | None = None  #:
    dwExtraInfo: PULong | None = None  #:


class HardwareInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-hardwareinput/"

    uMsg: DWord  #:
    wParamL: Word  #:
    wParamH: Word  #:


class Input(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-input/"

    class _U(c.Union): ...

    type: DWord  #:
    mi: MouseInput = c.anonymous(_U)  #:
    ki: KeybdInput = c.anonymous(_U)  #:
    hi: HardwareInput = c.anonymous(_U)  #:


class User32(ctypes.WinDLL):
    "Type of ``user32``."

    # TODO: calls to CDLL classes apparently do release the
    # GIL so we should be able to use that

    def __init__(self) -> None:
        super().__init__("user32")

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: Win32 DLL>"

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
"https://learn.microsoft.com/windows/win32/api/winuser/"


class InputType(IntEnum):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-input#members/"

    MOUSE, KEYBOARD, HARDWARE = range(3)
    "Option for ``type`` field of ``Input`` struct."


class ShiftState(IntFlag):
    "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-vkkeyscanw#return-value/"

    SHIFT, CTRL, ALT = autos(3)


class KeyEventF(IntFlag):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput#members/"

    DOWN, EXTENDED_KEY, UP, UNICODE, SCAN_CODE = 0, *autos(4)


class MouseEventF(IntFlag):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-mouseinput/"

    (MOVE, L_DOWN, L_UP, R_DOWN, R_UP, MID_DOWN, MID_UP,
     X_DOWN, X_UP, _1, _2, WHEEL, H_WHEEL, MOVE_NO_COALESCE,
     VIRTUAL_DESK, ABSOLUTE) = autos(16)  # fmt: off


class Mb(IntEnum):
    "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-messageboxw#parameters/"

    (OK, OK_CANCEL, ABORT_RETRY_IGNORE, YN_CANCEL, YN,
     RETRY_CANCEL,
     CANCEL_TRY_CONTINUE) = irange(0x0, 0x6, 0x1)  # fmt: off
    "Buttons option."

    (ICON_ERROR, ICON_QUESTION, ICON_WARNING,
     ICON_INFO) = irange(0x10, 0x40, 0x10)  # fmt: off
    "Icon picture option."
