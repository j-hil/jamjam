from __future__ import annotations

import ctypes
import logging
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import AbstractContextManager
from inspect import signature
from random import choice, random, randrange
from time import sleep, time
from typing import Generic, ParamSpec, Self, TypeVar

from jamjam import c
from jamjam._text import unwrap
from jamjam.classes import EzGetDesc
from jamjam.typing import Fn, MethodDef
from jamjam.win import (
    Id,
    Mb,
    MouseEventF,
    Wh,
    Wm,
    msg_loop,
    send_input,
)
from jamjam.winapi import (
    DWord,
    Int,
    LParam,
    LResult,
    MouseInput,
    WParam,
    kernel32,
    user32,
)

# TODO: make delay longer? mutate in debug mode?
# Also maybe detect key input from user too.
P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R", bound=c.BaseData | c.PyNative)

_log = logging.getLogger(__name__)
_PAUSE_SECS = 3
_HC_ACTION = 0
"Hook Code: Actionable."


def _start_window() -> Id:
    _log.info("Opened window.")

    response = user32.MessageBoxW(
        lpText=unwrap(f"""\
            The idler will randomly move your mouse.

            Taking control will pause the idler; after
            {_PAUSE_SECS} seconds it will resume. CONTINUE
            will pause the program until TRY-AGAIN is
            selected. CANCEL exits the program entirely.
        """),
        lpCaption="🐭 JamJam Mouse Idler",
        uType=Mb.CANCEL_TRY_CONT | Mb.TOPMOST,
    )
    return Id(response)


def _win_cfuncify(f: Fn) -> c.FuncPtr:
    sig = signature(f, eval_str=True)
    params = list(sig.parameters.values())

    argtypes = [c.extract(p.annotation) for p in params]
    rtype = c.extract(sig.return_annotation)
    return ctypes.WINFUNCTYPE(rtype, *argtypes)(f)


class _WinFnDesc(EzGetDesc[c.FuncPtr, T], Generic[T, P, R]):
    "Windows C-Function creation Descriptor"

    def __init__(self, f: MethodDef[T, P, R]) -> None:
        self.method_def = f
        # Apparently necessary to stash cfuncs to prevent gc
        # removing them. Prevents nasty bugs. See:
        # https://stackoverflow.com/questions/7901890
        self.cfuncs: dict[T, c.FuncPtr] = {}

    def instance_get(self, x: T) -> c.FuncPtr:
        cfunc = self.cfuncs.get(x)
        if cfunc is None:
            method = self.method_def.__get__(x)
            cfunc = self.cfuncs[x] = _win_cfuncify(method)
        return cfunc


class _MouseHook(AbstractContextManager):
    _thread: DWord | None = None
    _future: Future | None = None
    _user_control = True

    def __init__(self, executor: ThreadPoolExecutor) -> None:
        self.executor = executor
        self._last_user_input = time()

    def jump_mouse(self) -> None:
        secs = 1 + random()
        sleep(secs)

        dx = choice([-1, 1]) * randrange(10, 50)
        dy = choice([-1, 1]) * randrange(10, 50)
        mi = MouseInput(
            dx=dx, dy=dy, dwFlags=MouseEventF.MOVE
        )

        self._user_control = False
        if time() - self._last_user_input > _PAUSE_SECS:
            send_input(mi)
            _log.info(f"Moved {dx, dy} after {secs:.2}s.")
        self._user_control = True

    @_WinFnDesc
    def _hk(self, c: Int, wm: WParam, lp: LParam) -> LResult:
        """Low level mouse hook procedure.

        Takes the hook code, windows mouse message & a
        pointer to a MSLLHOOKSTRUCT (unused). See:
        https://learn.microsoft.com/windows/win32/winmsg/lowlevelmouseproc
        """
        _log.debug("LL mouse hook run")

        if c != _HC_ACTION or not self._user_control:
            pass
        elif wm in {Wm.M1_DOWN, Wm.M2_DOWN, Wm.MOUSE_MOVE}:
            self._last_user_input = time()
            _log.debug("User used mouse.")

        try:
            return user32.CallNextHookEx(None, c, wm, lp)
        except OSError as ex:
            if ex.winerror != 127:
                raise
            # This only occurs when debugging. Maybe related
            # to thread manipulation by debugger?
            _log.error(f"Ignored: {ex}")
        return 0

    def _start(self) -> None:
        self._thread = kernel32.GetCurrentThreadId()
        _log.info(f"Starting hook on thread {self._thread}")

        hook = user32.SetWindowsHookExW(
            Wh.MOUSE_LL,
            self._hk,
            kernel32.GetModuleHandleW(None),
            0,
        )
        msg_loop()
        user32.UnhookWindowsHookEx(hook)
        _log.info("Hook ended.")

    def __enter__(self) -> Self:
        self._future = self.executor.submit(self._start)
        return self

    def __exit__(self, *_: object) -> None:
        thread = self._thread
        if thread is None or self._future is None:
            msg = "Cannot stop hook before starting it."
            raise RuntimeError(msg)

        _log.info(f"Killing {thread=}")
        user32.PostThreadMessageW(thread, Wm.QUIT, 0, 0)
        self._future.result()

    start = __enter__
    stop = __exit__


def main() -> None:
    id = Id.TRY_AGAIN
    with ThreadPoolExecutor() as executor:
        while id in {Id.TRY_AGAIN, Id.CONTINUE}:
            window = executor.submit(_start_window)
            if id == Id.TRY_AGAIN:
                with _MouseHook(executor) as hook:
                    while not window.done():
                        hook.jump_mouse()
            id = window.result()


if __name__ == "__main__":
    logging.basicConfig(
        format=(
            "{asctime} {thread:<5} {levelname:<8} {msg}\n"
            "└────────────────────── {pathname}:{lineno}"
        ),
        style="{",
        datefmt="%X",
        stream=sys.stdout,
    )
    _log.setLevel(logging.INFO)

    main()
