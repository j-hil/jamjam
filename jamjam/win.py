"Access to the windows API."

# ruff: noqa: N802, N803, N815
from __future__ import annotations

import ctypes
from collections.abc import Callable
from ctypes.wintypes import (
    DWORD,
    HWND,
    INT,
    LONG,
    LPCWSTR,
    SHORT,
    SHORT,
    UINT,
    ULONG,
    WCHAR,
    WORD,
)
from enum import IntEnum, IntFlag
from typing import ClassVar, Self

from jamjam import c
from jamjam._lib.win import REQUIRED, imp_method
from jamjam.typing import maybe

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


def _super_init(parent: type[_T], self: _T) -> type[_T]:
    """Work around https://github.com/python/cpython/issues/73456/."""
    # cannot use super in subclasses due to 73456
    # cannot omit super params due to 73456
    # cannot use simple alias (eg `_super = super`) as type-checkers complain
    # cannot use Parent.__init__(...) as type-checkers complain
    return super(parent, self).__init__  # type: ignore[misc]


class IntMixin(c.SimpleData):
    name: str | None
    value: int

    _type_ = "O"
    """One of 'cbBhHiIlLdfuzZqQPXOv?g' required by `ctypes`.

    Overridden by subclass so choice irrelevant.
    "O" seems most appropriate, as used by `ctypes.py_object`.
    """

    nibble_grid: ClassVar = maybe(tuple[int, int])
    """Pair `(length, cols)`.

    If set there are `cols` explicit enumerals within each of nibble.
    Missing values are set as nameless enumerals.
    https://en.wikipedia.org/wiki/Nibble 🐭
    """

    @classmethod
    def _create_next_(
        cls, i: int, name: str, *_: object
    ) -> Self:
        if cls.nibble_grid:
            nibbles, cols = cls.nibble_grid
            base = 16
            if cols > base:
                raise ValueError
            index, digit = divmod(i, cols)
            if index >= nibbles:
                msg = (
                    f"{cls.__name__} has only {nibbles} nibbles. "
                    f"Found {name} in nibble {index} (indexed from 0)."
                )
                raise ValueError(msg)
            return cls(16**index + digit, name)
        raise AssertionError

    def __new__(
        cls, value: int, name: str | None = None
    ) -> Self:
        self = _super_new(cls)(cls, value)
        self.name = name
        return self

    def __or__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self.value | other.value)

    def __xor__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self.value ^ other.value)

    def __and__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self.value & other.value)

    def __hash__(self):
        return hash(self.value)


class InputType(IntEnum):
    """https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-input#members/."""

    MOUSE, KEYBOARD, HARDWARE = range(3)


class ShiftState(IntFlag):
    """https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-vkkeyscanw#return-value/."""

    value: int
    SHIFT, CTRL, ALT, HANKAKU, RESERVED1, RESERVED2 = (
        auto_batch(6)
    )


class KeyEventF(IntFlag):
    """https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput#members/."""

    value: int
    DOWN = 0
    EXTENDED_KEY, UP, UNICODE, SCAN_CODE = auto_batch(4)


class MouseEventF(IntFlag):
    """https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-mouseinput/."""

    value: int
    (
        (
            MOVE,
            L_DOWN,
            L_UP,
            R_DOWN,
            R_UP,
            MID_DOWN,
            MID_UP,
            X_DOWN,
            X_UP,
        ),
        (
            _1,
            _2,
            WHEEL,
            H_WHEEL,
            MOVE_NO_COALESCE,
            VIRTUAL_DESK,
            ABSOLUTE,
        ),
    ) = auto_batch(9, 7)


class Vk(IntEnum):
    """https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes/."""

    value: int
    _ignore_ = ("_", "_rws")  # type: ignore[assignment]
    _rws = (
        7,
        12,
        7,
        5,
        9,
        7,
        17,
        26,
        5,
        10,
        6,
        16,
        16,
        16,
        6,
        7,
        7,
        6,
        7,
        26,
        10,
        17,
        9,
    )

    (
        (
            MOUSE_L,
            MOUSE_R,
            CANCEL,
            MOUSE_WHEEL,
            MOUSE_X1,
            MOUSE_X2,
            _,
        ),
        (
            BACK,
            TAB,
            _,
            _,
            CLEAR,
            ENTER,
            _,
            _,
            SHIFT,
            CTRL,
            ALT,
            PAUSE,
        ),
        (CAPS, KANA, IME_ON, JUNJA, FINAL, KANJI, IME_OFF),
        (ESC, CONVERT, NON_CONVERT, ACCEPT, MODE_CHANGE),
        (
            SPACE,
            PAGE_UP,
            PAGE_DOWN,
            END,
            HOME,
            LEFT,
            UP,
            RIGHT,
            DOWN,
        ),
        (SELECT, PRINT, EXEC, PRINT_SCREEN, INS, DEL, HELP),
        (
            D0,
            D1,
            D2,
            D3,
            D4,
            D5,
            D6,
            D7,
            D8,
            D9,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ),
        (
            A,
            B,
            C,
            D,
            E,
            F,
            G,
            H,
            I,
            J,
            K,
            L,
            M,
            N,
            O,
            P,
            Q,
            R,
            S,
            T,
            U,
            V,
            W,
            X,
            Y,
            Z,
        ),
        (WIN_L, WIN_R, APPS, _, SLEEP),
        (NP0, NP1, NP2, NP3, NP4, NP5, NP6, NP7, NP8, NP9),
        (MULTIPLY, PLUS, SEPARATOR, MINUS, DOT, DIVIDE),
        (
            F1,
            F2,
            F3,
            F4,
            F5,
            F6,
            F7,
            F8,
            F9,
            F10,
            F11,
            F12,
            F13,
            F14,
            F15,
            F16,
        ),
        (
            F17,
            F18,
            F19,
            F20,
            F21,
            F22,
            F23,
            F24,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ),
        (
            NUM_LOCK,
            SCROLL,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ),
        (SHIFT_L, SHIFT_R, CTRL_L, CTRL_R, ALT_L, ALT_R),
        (
            BR_BACK,
            BR_FORWARD,
            BR_REFRESH,
            BR_STOP,
            BR_SEARCH,
            BR_FAV,
            BR_HOME,
        ),
        (
            VOL_MUTE,
            VOL_DOWN,
            VOL_UP,
            MEDIA_NEXT,
            MEDIA_PREV,
            MEDIA_STOP,
            MEDIA_PLAY,
        ),
        (MAIL, MEDIA, APP1, APP2, _, _),
        (
            OEM1,
            OEM_PLUS,
            OEM_COMMA,
            OEM_MINUS,
            OEM_DOT,
            OEM2,
            OEM3,
        ),
        (
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ),
        (OEM4, OEM5, OEM6, OEM7, OEM8, _, _, OEM102, _, _),
        (
            PROCESS,
            _,
            PACKET,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ),
        (
            ATTN,
            CR_SEL,
            EX_SEL,
            ER_EOF,
            PLAY,
            ZOOM,
            _,
            PA1,
            OEM_CLEAR,
        ),
    ) = auto_batch(*_rws)

    def event(self, event: KeyEventF) -> None:
        input = Input(
            InputType.KEYBOARD,
            ki=KeybdInput(wVk=self, dwFlags=event),
        )
        user32.SendInput(1, (Input * 1)(input), input.size())

    def down(self) -> None:
        self.event(KeyEventF.DOWN)

    def up(self) -> None:
        self.event(KeyEventF.UP)

    def tap(self) -> None:
        self.down()
        self.up()

    def __repr__(self) -> str:
        return f"<{self.name}: 0x{int(self):X}>"


def _super_new(
    cls: type[_T],
) -> Callable[[type[_T], int], _T]:
    """Work around https://github.com/python/cpython/issues/73456/."""
    # cannot use super in subclasses due to 73456
    # cannot omit super params due to 73456
    # cannot use simple alias (eg `_super = super`) as type-checkers complain
    # cannot use Parent.__init__(...) as type-checkers complain
    return super(cls, cls).__new__


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


# nice wrappers ########################################################################


def write(text: str) -> None:
    """Write the input alpha ascii text to where-ever the cursor is."""
    for char in text:
        byte1, byte2 = user32.VkKeyScanW(
            char
        ).value.to_bytes(2)
        key = Vk(byte2)
        shift = ShiftState(byte1)

        if shift is ShiftState.SHIFT:
            Vk.SHIFT.down()
            key.tap()
            Vk.SHIFT.up()
        elif shift is ShiftState(0):
            key.tap()
        else:
            msg = f"Unsupported shift state {shift!r}"
            raise NotImplementedError(msg)


def main() -> None:
    mouse_move = Input(
        InputType.MOUSE,
        mi=MouseInput(
            5000,
            5000,
            dwFlags=MouseEventF.MOVE | MouseEventF.ABSOLUTE,
        ),
    )
    x = user32.SendInput(
        1, (Input * 1)(mouse_move), Input.size()
    )
    print(x, type(x))


if __name__ == "__main__":
    user32.MessageBoxW(
        lpCaption="My Test",
        lpText="Hello! welcome to my first text box.",
        uType=Mb.OK_CANCEL | Mb.ICON_INFO,
    )
