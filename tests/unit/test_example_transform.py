# tests/unit/test_example_transform.py


def _example_clean_school_code(raw: str) -> str:
    """
    Example of a tiny, pure function you might later move
    into a real module (e.g. scripts/cleaning/school_codes.py).

    For now, this just demonstrates the unit test pattern.
    """
    return raw.strip().upper()


def test_example_clean_school_code_strips_and_uppercases():
    raw = "  k123  "
    expected = "K123"
    assert _example_clean_school_code(raw) == expected
