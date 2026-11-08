import pytest
from hypothesis import given
from hypothesis import strategies as st

from shelfwise.isbn import InvalidISBN, normalise


def with_check_digit(first_twelve: str) -> str:
    total = sum(
        int(digit) * (3 if index % 2 else 1) for index, digit in enumerate(first_twelve)
    )
    return first_twelve + str((10 - total % 10) % 10)


@pytest.mark.parametrize(
    "raw",
    ["9780441172719", "978-0-441-17271-9", "978 0 441 17271 9"],
)
def test_accepts_common_spellings(raw: str) -> None:
    assert normalise(raw) == "9780441172719"


ARABIC_INDIC_ISBN = "".join(chr(0x0660 + int(digit)) for digit in "9780441172719")


@pytest.mark.parametrize(
    "raw", ["", "123", "978044117271X", "9780441172710", ARABIC_INDIC_ISBN]
)
def test_rejects_bad_values(raw: str) -> None:
    with pytest.raises(InvalidISBN):
        normalise(raw)


@given(st.text(alphabet="0123456789", min_size=12, max_size=12))
def test_any_correct_check_digit_is_accepted(first_twelve: str) -> None:
    isbn = with_check_digit(first_twelve)
    assert normalise(isbn) == isbn


@given(st.text(max_size=40))
def test_never_crashes_on_arbitrary_text(raw: str) -> None:
    try:
        result = normalise(raw)
    except InvalidISBN:
        return
    assert len(result) == 13


@given(st.text(alphabet=st.characters(categories=["Nd"]), min_size=13, max_size=13))
def test_only_ascii_digits_are_accepted(raw: str) -> None:
    try:
        result = normalise(raw)
    except InvalidISBN:
        return
    assert result.isascii()
