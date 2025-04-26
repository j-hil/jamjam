from jamjam import c


def test_struct() -> None:
    class A(c.Struct):
        field1: c.Int
        field2: c.Str

    struct = A(field1=10, field2="test")
    assert isinstance(struct, A)
    assert struct.field1 == 10
    assert struct.field2 == "test"
