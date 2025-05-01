"Helpers for ``jamjam``'s tests."

try:
    from pytest import FixtureRequest, fixture, mark, skip
except ImportError as ex:
    _msg = f"Only import {__name__}  during testing."
    raise ImportError(_msg) from ex


@fixture
def manual_only_fixture(request: FixtureRequest) -> None:
    if request.session.items == [request.node]:
        return
    reason = "Test only runs in solo; never in a suite."
    skip(reason)


manual_only = mark.usefixtures(manual_only_fixture.__name__)
"Mark a test to only run when manually triggered."
