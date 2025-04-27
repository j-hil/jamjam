from time import sleep

from jamjam.win import IntMixin, Mb, Vk, write


def check_write() -> None:
    Vk.WIN_L.tap()
    sleep(1)

    write("notepad")
    sleep(1)

    Vk.ENTER.tap()
    sleep(1)

    write("Hello! Now I can write anything!")


def test_enum_type_attribute() -> None:
    # check IntMixin's attribute is overridden
    assert Mb._type_ != IntMixin._type_


def test_flag_enum() -> None:
    assert repr(Mb.YN) == "<Mb.YN>"


if __name__ == "__main__":
    check_write()
