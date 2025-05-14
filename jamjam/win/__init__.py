"""Interaction with Windows OS.

The 'top level' ``jamjam.win`` provides 'nice' pythonic
wrappers. For a close map to the native windows API use
the ``jamjam.win.api`` submodule, on which this is built.
"""

from enum import IntEnum

from jamjam.win.api import (
    Input,
    InputType,
    KeybdInput,
    KeyEventF,
    MouseEventF,
    MouseInput,
    ShiftState,
    user32,
)


class Vk(IntEnum):
    """Virtual Key enumeration & interaction.

    https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes/
    """

    # The names are chosen to be short but (hopefully) clear.
    # Those of the form _HH are undefined/reserved.
    # Mark enumerals as private as else docs too verbose.
    #: :meta private:
    (NULL, MOUSE1, MOUSE2, CANCEL, MOUSE_WHL, MOUSE_X1,
     MOUSE_X2, _07, BACK, TAB, _0A, _0B, CLEAR, ENTER, _0E,
     _0F, SHIFT, CTRL, ALT, PAUSE, CAPS, IME_KANA, IME_ON,
     IME_JUNJA, IME_FINAL, IME_KANJI, IME_OFF, ESC,
     IME_CONVERT, IME_NON_CONVERT, IME_ACCEPT,
     IME_MODE_CHANGE, SPACE, PG_UP, PG_DN, END, HOME, LEFT,
     UP, RIGHT, DOWN, SELECT, PRINT, EXEC, PRT_SCN, INS, DEL,
     HELP, D0, D1, D2, D3, D4, D5, D6, D7, D8, D9, _3A, _3B,
     _3C, _3D, _3E, _3F, _40, A, B, C, D, E, F, G, H, I, J,
     K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, WIN_L,
     WIN_R, APPS, _5E, SLEEP, NP0, NP1, NP2, NP3, NP4, NP5,
     NP6, NP7, NP8, NP9, TIMES, PLUS, SEP, MINUS, DOT,
     DIVIDE, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11,
     F12, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22,
     F23, F24, _88, _89, _8A, _8B, _8C, _8D, _8E, _8F,
     NUM_LOCK, SCR_LOCK, _92, _93, _94, _95, _96, _97, _98,
     _99, _9A, _9B, _9C, _9D, _9E, _9F, SHIFT1, SHIFT2,
     CTRL1, CTRL2, ALT1, ALT2, BR_BACK, BR_FWD, BR_REFRESH,
     BR_STOP, BR_SEARCH, BR_FAVS, BR_HOME, VOL_MUTE,
     VOL_DOWN, VOL_UP, MEDIA_NEXT, MEDIA_PREV, MEDIA_STOP,
     MEDIA_PLAY, MAIL, MEDIA_SELECT, APP1, APP2, _B8, _B9,
     OEM1, OEM_PLUS, OEM_COMMA, OEM_MINUS, OEM_DOT, OEM2,
     OEM3, _C1, _C2, _C3, _C4, _C5, _C6, _C7, _C8, _C9, _CA,
     _CB, _CC, _CD, _CE, _CF, _D0, _D1, _D2, _D3, _D4, _D5,
     _D6, _D7, _D8, _D9, _DA, OEM4, OEM5, OEM6, OEM7, OEM8,
     _EO, _E1, OEM_102, _E3, _E4, IME_PROCESS, _E6, PACKET,
     _E8, _E9, _EA, _EB, _EC, _ED, _EE, _EF, _F0, _F1, _F2,
     _F3, _F4, _F5, ATTN, CR_SEL, EX_SEL, ERASE_EOF, PLAY,
     ZOOM, NO_NAME, PA1, OEM_CLEAR) = range(0xFF)  # fmt: off

    def event(self, event: KeyEventF) -> None:
        inp = Input(
            type=InputType.KEYBOARD,
            ki=KeybdInput(wVk=self, dwFlags=event),
        )
        user32.SendInput(1, (Input * 1)(inp), inp.size())

    def down(self) -> None:
        self.event(KeyEventF.DOWN)

    def up(self) -> None:
        self.event(KeyEventF.UP)

    def tap(self) -> None:
        self.down()
        self.up()

    def __repr__(self) -> str:
        return f"<{self.name}: 0x{int(self):X}>"


def write(text: str) -> None:
    "Write (ascii) ``text`` where-ever the cursor is."
    for char in text:
        short = user32.VkKeyScanW(char)
        byte1, byte2 = short.value.to_bytes(2)
        key = Vk(byte2)
        state = ShiftState(byte1)

        if state is ShiftState.SHIFT:
            Vk.SHIFT.down()
            key.tap()
            Vk.SHIFT.up()
        elif state is ShiftState(0):
            key.tap()
        else:
            msg = f"Unsupported shift state {state!r}"
            raise NotImplementedError(msg)


def send_input(*inputs: MouseInput | KeybdInput) -> int:
    "Send user input, auto handling union discrimination."
    n = len(inputs)
    structs = (Input * n)()
    for i, input in enumerate(inputs):
        if isinstance(input, MouseInput):
            struct = Input(type=InputType.MOUSE, mi=input)
        else:
            struct = Input(type=InputType.KEYBOARD, ki=input)
        structs[i] = struct
    return user32.SendInput(n, structs, Input.size()).value


def _main() -> None:
    mouse_move = Input(
        type=InputType.MOUSE,
        mi=MouseInput(
            dx=5000,
            dy=5000,
            dwFlags=MouseEventF.MOVE | MouseEventF.ABSOLUTE,
        ),
    )
    user32.SendInput(
        1, (Input * 1)(mouse_move), Input.size()
    )


if __name__ == "__main__":
    _main()
