# tests/unit/test_sanity_unit.py
def test_basic_math_sanity():
    """Simple sanity check so CI immediately tells us if pytest is wired."""
    assert 1 + 1 == 2
