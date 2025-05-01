import ctypes

from jamjam import c


def test_extract() -> None:
    ctype = c.extract(c.Str)
    assert ctype == ctypes.c_wchar_p

    ctype = c.extract(c.Array[ctypes.c_bool])
    assert ctype == c.Array


def test_struct() -> None:
    class A(c.Struct):
        field1: c.Int
        field2: c.Str

    struct = A(field1=10, field2="test")
    assert isinstance(struct, A)
    assert struct.field1 == 10
    assert struct.field2 == "test"


def test_anonymous() -> None:
    class B(c.Struct):
        class _U(c.Union): ...

        disc: c.Int
        anonymous1: c.Str = c.anonymous(_U)
        anonymous2: c.Int = c.anonymous(_U)

    struct = B(disc=1, anonymous1="hello")
    assert isinstance(struct, B)
    assert struct.disc == 1
    assert struct.anonymous1 == "hello"
