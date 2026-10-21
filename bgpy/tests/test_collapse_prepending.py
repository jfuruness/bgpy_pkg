import pytest

from bgpy.shared.utils import collapse_prepending


@pytest.mark.unit_tests
@pytest.mark.parametrize(
    ("as_path", "expected"),
    [
        ((), ()),
        ((1,), (1,)),
        ((1, 1, 1), (1,)),
        ((1, 1, 2, 3, 3), (1, 2, 3)),
        ((1, 2, 2, 2, 3), (1, 2, 3)),
        # Collapsing, not deduplicating
        ((1, 2, 1), (1, 2, 1)),
        ((1, 1, 2, 1, 1), (1, 2, 1)),
    ],
)
def test_collapse_prepending(as_path, expected):
    assert collapse_prepending(as_path) == expected


@pytest.mark.unit_tests
def test_collapse_prepending_returns_same_tuple_without_prepending():
    """The common case must not allocate a new tuple"""

    as_path = (1, 2, 3)
    assert collapse_prepending(as_path) is as_path
