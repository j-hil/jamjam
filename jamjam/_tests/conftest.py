from pytest import FixtureRequest, fixture, mark, skip


@fixture
def _manual_only(request: FixtureRequest) -> None:
    if request.session.items == [request.node]:
        return
    reason = "Test only runs in solo; never in a suite."
    skip(reason)


manual_only = mark.usefixtures(_manual_only.__name__)
"Mark a test to only run when manually triggered."
