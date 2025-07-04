from pytest import raises

from jamjam._testing import manual_only
from jamjam.win import InputType, Mb, Vk, write
from jamjam.winapi import (
    Input,
    KeybdInput,
    MouseInput,
    kernel32,
    user32,
)


@manual_only
def test_message_box() -> None:
    "Message box should pop up."
    r = user32.MessageBoxW(
        lpCaption="My Test",
        lpText="Close this box to complete the test!",
        uType=Mb.OK_CANCEL | Mb.ICON_INFO,
    )
    assert isinstance(r, int)


@manual_only
def test_send_input() -> None:
    "Should type out 'a' where cursor is."
    press_a = Input(
        type=InputType.KEYBOARD, ki=KeybdInput(wVk=Vk.A)
    )
    user32.SendInput(1, (Input * 1)(press_a), Input.size())


@manual_only
def test_vk() -> None:
    "Should type out 'a' where cursor is."
    Vk.A.down()


@manual_only
def test_write() -> None:
    "Writes text where cursor is."
    write("Hello!")


def test_method_works() -> None:
    module = kernel32.GetModuleHandleW(None)
    assert module is not None


def test_method_erroring() -> None:
    with raises(OSError) as ex_info:  # noqa: PT011
        user32.GetWindowTextW(None, "", 256)
    assert ex_info.value.winerror == 1400
    assert ex_info.value.strerror == "Invalid window handle."


def test_mi_struct() -> None:
    MouseInput(dx=1, dy=2)
