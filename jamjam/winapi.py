"""Access to the Windows API.

This module is intentionally written in a way to make it
easy to auto-generate, should I ever need to.
More 'bespoke' wrappers are in ``jamjam.win``.
"""

# ruff: noqa: N802, N803, N815, PLR0917, PLR0913
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
    PDWORD,
    SHORT,
    UINT,
    ULONG,
    WCHAR,
    WORD,
    WPARAM,
)
from functools import wraps
from inspect import signature
from typing import Annotated, ParamSpec, TypeVar, cast

from jamjam import c
from jamjam.typing import MethodDef

P = ParamSpec("P")
T = TypeVar("T")
D = TypeVar("D", bound=ctypes.CDLL)
R = TypeVar("R", bound=c.BaseData | c.PyNative)

# NOTE: my poor understanding of VOID pointers suggests
# that type(NULL) is treated as a super-type of any pointer
# while NULL itself is treated as an instance of any pointer.
VoidPtr = c.Pointer[c.Data] | ctypes.c_void_p | None
ULongPtr = c.Pointer[ULONG]
PDWORD_PTR = c.Pointer[PDWORD]
FARPROC = ctypes.c_void_p

# Typing both the python type and the ctype is
# probably too hard - especially with `converters` currently
# unsupported (https://github.com/python/mypy/issues/17547)
# and ctype's unconventional auto-unpacking. Hence for now
# only support the python type.
# fmt: off
HWnd        = Annotated[VoidPtr,            HWND        ]
LpCwStr     = Annotated[str | None,         LPCWSTR     ]
UInt        = Annotated[int,                UINT        ]
Int         = Annotated[int,                INT         ]
Long        = Annotated[int,                LONG        ]
DWord       = Annotated[int,                DWORD       ]
Word        = Annotated[int,                WORD        ]
WChar       = Annotated[str,                WCHAR       ]
LParam      = Annotated[int,                LPARAM      ]
WParam      = Annotated[int,                WPARAM      ]
HHook       = Annotated[VoidPtr,            HHOOK       ]
LResult     = Annotated[int,                LPARAM      ]
HInstance   = Annotated[VoidPtr,            HINSTANCE   ]
Short       = Annotated[int,                SHORT       ]
Bool        = Annotated[int,                BOOL        ]
HModule     = Annotated[VoidPtr,            HMODULE     ]
DWordPtrPtr = Annotated[PDWORD_PTR | None,  PDWORD_PTR  ]
FarProc     = Annotated[VoidPtr,            FARPROC     ]
# fmt: on
# https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types


class MouseInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-mouseinput/"

    # fmt: off
    dx:             Long                        #:
    dy:             Long                        #:
    mouseData:      DWord       = c.OPTIONAL    #:
    dwFlags:        DWord       = c.OPTIONAL    #:
    time:           DWord       = c.OPTIONAL    #:
    dwExtraInfo:    ULongPtr    = c.OPTIONAL    #:


class KeybdInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput/"

    # fmt: off
    wVk:            Word                        #:
    wScan:          Word        = c.OPTIONAL    #:
    dwFlags:        DWord       = c.OPTIONAL    #:
    time:           DWord       = c.OPTIONAL    #:
    dwExtraInfo:    ULongPtr    = c.OPTIONAL    #:


class HardwareInput(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-hardwareinput/"

    # fmt: off
    uMsg:       DWord   #:
    wParamL:    Word    #:
    wParamH:    Word    #:


class Input(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-input/"

    class _U(c.Union): ...

    # fmt: off
    type:   DWord                              #:
    mi:     MouseInput      = c.anonymous(_U)  #:
    ki:     KeybdInput      = c.anonymous(_U)  #:
    hi:     HardwareInput   = c.anonymous(_U)  #:


class Point(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/windef/ns-windef-point"

    x: Long = c.OPTIONAL  #:
    y: Long = c.OPTIONAL  #:


class Msg(c.Struct):
    "https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-msg"

    # fmt: off
    hWnd:       HWnd    = c.OPTIONAL  #:
    message:    UInt    = c.OPTIONAL  #:
    wParam:     WParam  = c.OPTIONAL  #:
    lParam:     LParam  = c.OPTIONAL  #:
    time:       DWord   = c.OPTIONAL  #:
    pt:         Point   = c.OPTIONAL  #:


def _errcheck(
    result: c.BaseData | c.PyNative,
    f: c.FuncPtr,
    args: tuple[c.BaseData, ...],
) -> c.Data:
    _ = args, f
    if errno := ctypes.get_last_error():
        raise ctypes.WinError(errno)
    if isinstance(result, c.PyNative):
        # Seems stubs for `CFuncPtr.errcheck` don't capture
        # ctypes's special casing of PyNative hence cast.
        result = cast(c.Data, result)
    elif not isinstance(result, c.Data):
        msg = f"Expected c-type return. Got value {result}."
        raise TypeError(msg)
    return result


def _imp_method(f: MethodDef[D, P, R]) -> MethodDef[D, P, R]:
    "Implement a WinDLL method from it's name & typing."
    method_name = f.__name__

    @wraps(f)
    def new_method_defn(
        self: D, /, *args: P.args, **kwargs: P.kwargs
    ) -> R:
        cfunc = self[method_name]
        method = getattr(self, method_name)
        sig = signature(method, eval_str=True)
        params = sig.parameters.values()
        argtypes = [c.extract(p.annotation) for p in params]

        cfunc.argtypes = argtypes
        cfunc.restype = c.extract(sig.return_annotation)
        cfunc.errcheck = _errcheck

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        missing = [
            param
            for param, arg in bound.arguments.items()
            if arg is c.REQUIRED
        ]
        if missing:
            msg = f"Required param(s) {missing} missing."
            raise TypeError(msg)
        return cfunc(*bound.arguments.values())

    return new_method_defn


class _WinDLL(ctypes.WinDLL):
    def __init__(self) -> None:
        self.name = f"{self.__class__.__name__.upper()}"
        super().__init__(self.name, use_last_error=True)

    def __repr__(self) -> str:
        return f"<WinDLL: {self.name}>"


class User32(_WinDLL):
    "Type of ``user32`` DLL."

    @_imp_method
    def MessageBoxW(
        self,
        hWnd: HWnd = None,
        lpText: LpCwStr = None,
        lpCaption: LpCwStr = None,
        uType: UInt = c.REQUIRED,
    ) -> Int:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-messageboxw/"
        raise NotImplementedError

    @_imp_method
    def SendInput(
        self,
        cInputs: UInt,
        pInputs: c.Array[Input],
        cbSize: Int,
    ) -> UInt:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-sendinput/"
        raise NotImplementedError

    @_imp_method
    def VkKeyScanW(self, ch: WChar) -> Short:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-vkkeyscanw/"
        raise NotImplementedError

    @_imp_method
    def CallNextHookEx(
        self,
        hhk: HHook,
        nCode: Int,
        wParam: WParam,
        lParam: LParam,
    ) -> LResult:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex"
        raise NotImplementedError

    @_imp_method
    def SetWindowsHookExW(
        self,
        idHook: Int,
        lpfn: c.FuncPtr,
        hmod: HInstance,
        dwThreadId: DWord,
    ) -> HHook:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexw"
        raise NotImplementedError

    @_imp_method
    def GetMessageW(
        self,
        lpMsg: c.Pointer[Msg],
        hWnd: HWnd,
        wMsgFilterMin: UInt,
        wMsgFilterMax: UInt,
    ) -> Bool:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmessagew"
        raise NotImplementedError

    @_imp_method
    def TranslateMessage(
        self, lpMsg: c.Pointer[Msg]
    ) -> Bool:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-translatemessage"
        raise NotImplementedError

    @_imp_method
    def DispatchMessageW(
        self, lpMsg: c.Pointer[Msg]
    ) -> LResult:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-dispatchmessagew"
        raise NotImplementedError

    @_imp_method
    def UnhookWindowsHookEx(self, hhk: HHook) -> Bool:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-unhookwindowshookex"
        raise NotImplementedError

    @_imp_method
    def GetWindowTextW(
        self, hWnd: HWnd, lpString: LpCwStr, nMaxCount: Int
    ) -> Int:
        "https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtextw"
        raise NotImplementedError

    @_imp_method
    def PostThreadMessageW(
        self,
        idThread: DWord,
        Msg: UInt,
        wParam: WParam,
        lParam: LParam,
    ) -> Bool:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postthreadmessagew"
        raise NotImplementedError

    @_imp_method
    def SendMessageW(
        self,
        hWnd: HWnd,
        Msg: UInt,
        wParam: WParam,
        lParam: LParam,
    ) -> LResult:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendmessagew"
        raise NotImplementedError

    @_imp_method
    def SendMessageTimeoutW(
        self,
        hWnd: HWnd,
        Msg: UInt,
        wParam: WParam,
        lParam: LParam,
        fuFlags: UInt,
        uTimeout: UInt,
        lpdwResult: DWordPtrPtr = None,
    ) -> LResult:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendmessagetimeoutw"
        raise NotImplementedError

    @_imp_method
    def GetCursorPos(
        self, lpPoint: c.Pointer[Point]
    ) -> Bool:
        "https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorpos"
        raise NotImplementedError

    @_imp_method
    def SetCursorPos(self, X: Int, Y: Int) -> Bool:
        "http://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setcursorpos"
        raise NotImplementedError


class Kernel32(_WinDLL):
    "Type of ``kernel32`` DLL."

    @_imp_method
    def GetModuleHandleW(
        self, lpModuleName: LpCwStr
    ) -> HModule:
        "https://learn.microsoft.com/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlew"
        raise NotImplementedError

    @_imp_method
    def GetCurrentThreadId(self) -> DWord:
        "https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentthreadid"
        raise NotImplementedError

    @_imp_method
    def GetProcAddress(
        self, hModule: HModule, lpProcName: LpCwStr
    ) -> FarProc:
        "https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress"
        raise NotImplementedError


kernel32 = Kernel32()
"https://learn.microsoft.com/windows/win32/api/_base/"
user32 = User32()
"https://learn.microsoft.com/windows/win32/api/winuser/"
