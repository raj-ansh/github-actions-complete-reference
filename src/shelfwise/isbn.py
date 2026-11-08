"""ISBN-13 validation and normalisation."""


class InvalidISBN(ValueError):
    """Raised when a string is not a valid ISBN-13."""


def normalise(raw: str) -> str:
    """Return the 13 digits of ``raw``, or raise ``InvalidISBN``.

    Hyphens and spaces are accepted because booksellers paste ISBNs from
    many sources. The check digit is always verified.
    """
    digits = raw.replace("-", "").replace(" ", "")
    if len(digits) != 13 or not (digits.isascii() and digits.isdigit()):
        raise InvalidISBN(f"not a 13-digit ISBN: {raw!r}")
    total = sum(
        int(digit) * (3 if index % 2 else 1) for index, digit in enumerate(digits)
    )
    if total % 10 != 0:
        raise InvalidISBN(f"bad check digit: {raw!r}")
    return digits
