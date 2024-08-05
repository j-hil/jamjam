from jamjam.classes import Singleton, easy_repr


def test_singleton() -> None:
    class A(Singleton):
        pass

    class B(Singleton):
        pass

    assert A() is A()
    assert B() is B()
    assert A() is not B()


def test_easy_repr() -> None:
    s = easy_repr("", 1, 2, hello=3, world=4)
    assert s == "str(1, 2, hello=3, world=4)"
