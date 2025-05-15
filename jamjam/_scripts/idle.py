import ctypes
from concurrent.futures import ThreadPoolExecutor
from ctypes.wintypes import INT, LONG, LPARAM, WPARAM
from random import choice, random, randrange
from time import sleep

from jamjam.win import send_input
from jamjam.win.api import (
    Mb,
    MouseEventF,
    MouseInput,
    Msg,
    Wh,
    Wm,
    kernel32,
    user32,
)


def _start_window() -> int:
    response = user32.MessageBoxW(
        lpText="Mouse Idler is active. Press OK to disable.",
        lpCaption="JamJam Mouse Idler",
        uType=Mb.OK,
    )
    return response


def main() -> None:
    with ThreadPoolExecutor() as executor:
        future = executor.submit(_start_window)
        while future.running():
            seconds = 1 + random()
            sleep(seconds)

            dx = choice([-1, 1]) * randrange(10, 50)
            dy = choice([-1, 1]) * randrange(10, 50)
            mi = MouseInput(
                dx=dx, dy=dy, dwFlags=MouseEventF.MOVE
            )
            send_input(mi)
            print(f"Moved {dx, dy} after {seconds:.2} secs.")


@ctypes.WINFUNCTYPE(LONG, INT, WPARAM, LPARAM)  # type: ignore[misc]
def _ll_mouse_proc(code: int, wm: int, long: int) -> int:
    """Low level mouse hook procedure.

    https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc.
    """
    hc_action = 0  # const, see link in docstring
    if code == hc_action:
        if wm == Wm.LBUTTON_DOWN:
            print("Left mouse button clicked!")
        elif wm == Wm.RBUTTON_DOWN:
            print("Right mouse button clicked!")
    return user32.CallNextHookEx(None, code, wm, long)


# TODO: finish this addition to the idle app
def do_mouse_hook() -> None:
    hook = user32.SetWindowsHookExW(
        Wh.MOUSE_LL,
        _ll_mouse_proc,
        kernel32.GetModuleHandleW(None),
        0,
    )

    # Put this in a try capture:
    print("Enter a message loop to keep the hook active ...")
    msg_ptr = Msg().byref()  # type: ignore[call-arg]
    while not user32.GetMessageW(msg_ptr, None, 0, 0):
        user32.TranslateMessage(msg_ptr)
        user32.DispatchMessageW(msg_ptr)
    user32.UnhookWindowsHookEx(hook)


if __name__ == "__main__":
    main()
