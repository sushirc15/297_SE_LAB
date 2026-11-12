from hypothesis import example, given, settings, strategies as st
from income_tax_parser import clean_pan, parse_amount, parse_tax_slab

EDGE_INPUTS = (
    st.text()
    | st.none()
    | st.integers()
    | st.floats(allow_nan=True)
    | st.booleans()
)


@settings(max_examples=200)
@given(EDGE_INPUTS)
@example(None)
@example("")
@example("   ")
@example("abcde 1234f")
@example("!@#$%")
def test_clean_pan_no_crash(s):
    try:
        result = clean_pan(s)
    except Exception as e:
        assert False, f"clean_pan crashed with: {e}"
    if result is not None:
        assert isinstance(result, str)
        assert result == result.upper()
        assert not any(ch.isspace() for ch in result)


@settings(max_examples=200)
@given(EDGE_INPUTS)
@example(None)
@example("")
@example("Rs ")
@example("Rs 12,50,000")
@example("-500")
@example("9" * 5000)
def test_parse_amount_no_crash(s):
    try:
        result = parse_amount(s)
    except Exception as e:
        assert False, f"parse_amount crashed with: {e}"
    if result is not None:
        assert isinstance(result, int) and not isinstance(result, bool)
        assert result >= 0


@settings(max_examples=200)
@given(EDGE_INPUTS | st.from_regex(r".*[-:].*", fullmatch=True))
@example(None)
@example("")
@example(":")
@example("250000-500000:5")
@example("500000-250000:5")
@example("100-200:5:10")
@example("100-200:150")
def test_parse_tax_slab_no_crash(s):
    try:
        result = parse_tax_slab(s)
    except Exception as e:
        assert False, f"parse_tax_slab crashed with: {e}"
    if result is not None:
        assert isinstance(result, tuple) and len(result) == 3
        low, high, rate = result
        assert 0 <= low < high
        assert 0 <= rate <= 100
