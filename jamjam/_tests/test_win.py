from jamjam._tests.conftest import manual_only
from jamjam.win import Input, KeybdInput, Mb, user32


@manual_only
def test_message_box() -> None:
    "Message box should pop up."
    user32.MessageBoxW(
        lpCaption="My Test",
        lpText="Close this box to complete the test!",
        uType=Mb.OK_CANCEL | Mb.ICON_INFO,
    )


@manual_only
def test_send_input() -> None:
    "Should type out 'a' where cursor is."
    # TODO: move this into API?
    input_keyboard = 1
    vk_a = 0x41

    press_a = Input(
        type=input_keyboard, ki=KeybdInput(wVk=vk_a)
    )
    user32.SendInput(1, (Input * 1)(press_a), Input.size())
