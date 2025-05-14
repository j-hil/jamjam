"""Access to the windows API.

This module is intentionally written in a way to make it
easy to auto-generate, should I ever need to.
More 'bespoke' wrappers are in ``jamjam.win``.
"""

# ruff: noqa: N802, N803, N815
from __future__ import annotations

import ctypes
from ctypes.wintypes import (
    BOOL,
    DWORD,
    HHOOK,
    HINSTANCE,
    HMODULE,
    HWND,
    INT,
    LONG,
    LPARAM,
    LPCWSTR,
    SHORT,
    UINT,
    ULONG,
    WCHAR,
    WORD,
    WPARAM,
)
from enum import IntEnum, IntFlag

from jamjam import c
from jamjam._lib.win import REQUIRED, imp_method
from jamjam.classes import autos
from jamjam.iter import irange

# TODO: supporting both the python type and the ctype is
# probably too hard - especially with `converters` currently
# unsupported (https://github.com/python/mypy/issues/17547)
# and ctype's unconventional auto-unpacking. Hence
# experiment with only supporting the python type and see how
# that goes.
HWnd = HWND | None  #:
LpCwStr = LPCWSTR | str | None  #:
UInt = int | UINT  #:
Int = int | INT  #:
Long = int | LONG  #:
DWord = int | DWORD  #:
Word = int | WORD  #:
PULong = c.Pointer[ULONG]  #:
WChar = str | WCHAR  #:
LParam = int | LPARAM
WParam = int | WPARAM
HHook = HHOOK | None
LRESULT = LPARAM
LResult = int | LRESULT
HInstance = HINSTANCE | None


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


class Point(c.Struct):
    "https://learn.microsoft.com/en-us/windows/win32/api/windef/ns-windef-point"

    x: Long
    y: Long


class Msg(c.Struct):
    "https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msg"

    hWnd: HWnd
    message: UInt
    wParam: WParam
    lParam: LParam
    time: DWord
    pt: Point


# TODO: sync kernel32 & user32 defs with new base class
class User32(ctypes.WinDLL):
    "Type of ``user32`` DLL."

    def __init__(self) -> None:
        super().__init__("user32", use_last_error=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: Win32 DLL>"

    @imp_method
    def MessageBoxW(
        self,
        hWnd: HWnd = None,
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

    @imp_method
    def CallNextHookEx(
        self,
        hhk: HHook,
        nCode: Int,
        wParam: WParam,
        lParam: LParam,
    ) -> LRESULT:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex"
        raise NotImplementedError

    @imp_method
    def SetWindowsHookExW(
        self,
        idHook: Int,
        lpfn: c.FuncPtr,
        hmod: HInstance,
        dwThreadId: DWord,
    ) -> HHOOK:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexw"
        raise NotImplementedError

    @imp_method
    def GetMessageW(
        self,
        lpMsg: c.Pointer[Msg],
        hWnd: HWnd,
        wMsgFilterMin: UInt,
        wMsgFilterMax: UInt,
    ) -> BOOL:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessagew"
        raise NotImplementedError

    @imp_method
    def TranslateMessage(
        self, lpMsg: c.Pointer[Msg]
    ) -> BOOL:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-translatemessage"
        raise NotImplementedError

    @imp_method
    def DispatchMessageW(
        self, lpMsg: c.Pointer[Msg]
    ) -> LResult:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-dispatchmessagew"
        raise NotImplementedError

    @imp_method
    def UnhookWindowsHookEx(self, hhk: HHook) -> BOOL:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwindowshookex"
        raise NotImplementedError

    @imp_method
    def GetWindowTextW(
        self,
        hWnd: HWnd,
        lpString: c.Pointer[WCHAR] | c.Array[WCHAR] | str,
        nMaxCount: Int,
    ) -> INT:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowtextw"
        raise NotImplementedError


class Kernel32(ctypes.WinDLL):
    "Type of ``kernel32`` DLL."

    def __init__(self) -> None:
        super().__init__("kernel32")

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: Win32 DLL>"

    @imp_method
    def GetModuleHandleW(
        self, lpModuleName: LpCwStr
    ) -> HMODULE:
        "https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlew"
        raise NotImplementedError


kernel32 = Kernel32()
"https://learn.microsoft.com/en-us/windows/win32/api/_base/"
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


class Wh(IntEnum):
    "https://learn.microsoft.com/en-gb/windows/win32/api/winuser/nf-winuser-setwindowshookexw#parameters"

    (MSG, _0, _1, KEYBOARD, GET_MSG, CALL_WND, CBT, SYS_MSG,
     MOUSE, _8, DEBUG, SHELL, FOREGROUND_IDLE,
     CALL_WND_RETURN, KEYBOARD_LL, MOUSE_LL) = irange(-1, 14)  # fmt: off


class Wm(IntEnum):
    """Windows Message.

    https://learn.microsoft.com/en-us/windows/win32/inputdev/mouse-input-notifications
    """

    LBUTTON_DOWN = 0x0201
    RBUTTON_DOWN = 0x0204
