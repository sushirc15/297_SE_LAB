import re

_PAN_RE = re.compile(r"^[A-Z0-9]+$", re.ASCII)
_AMOUNT_RE = re.compile(
    r"^(?:rs\.?|₹)?\s*([0-9]+|[0-9]{1,3}(?:,[0-9]{2,3})+)$",
    re.IGNORECASE | re.ASCII,
)
_SLAB_RE = re.compile(
    r"^\s*([0-9]{1,30})\s*-\s*([0-9]{1,30})\s*:\s*([0-9]{1,3})\s*$",
    re.ASCII,
)
_MAX_INPUT_LEN = 128
_MAX_DIGITS = 30


def clean_pan(pan):
    """
    Removes all whitespace from a PAN and upper-cases it.
    Returns None for non-string, empty, or non-alphanumeric inputs.
    """
    if not isinstance(pan, str):
        return None
    cleaned = "".join(pan.split()).upper()
    if not cleaned or len(cleaned) > _MAX_INPUT_LEN or not _PAN_RE.fullmatch(cleaned):
        return None
    return cleaned


def parse_amount(text):
    """
    Converts an amount such as 'Rs 12,50,000' into a non-negative int.
    Returns None for non-string, malformed, negative, or oversized inputs.
    """
    if not isinstance(text, str):
        return None
    stripped = text.strip()
    if not stripped or len(stripped) > _MAX_INPUT_LEN:
        return None
    match = _AMOUNT_RE.fullmatch(stripped)
    if not match:
        return None
    digits = match.group(1).replace(",", "")
    if len(digits) > _MAX_DIGITS:
        return None
    return int(digits)


def parse_tax_slab(line):
    """
    Parses 'LOW-HIGH:RATE' into a (low, high, rate) tuple of ints.
    Validates 0 <= low < high and 0 <= rate <= 100.
    Returns None for non-string or invalid inputs.
    """
    if not isinstance(line, str) or len(line) > _MAX_INPUT_LEN:
        return None
    match = _SLAB_RE.fullmatch(line)
    if not match:
        return None
    low = int(match.group(1))
    high = int(match.group(2))
    rate = int(match.group(3))
    if low >= high or rate > 100:
        return None
    return low, high, rate


def _safe_input(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None


def main():
    print("==== Running clean_pan ====")
    value = _safe_input("Enter a PAN (e.g. abcde 1234f): ")
    cleaned_pan = clean_pan(value)
    if cleaned_pan is None:
        print("Cleaned PAN: Invalid PAN input")
    else:
        print("Cleaned PAN:", cleaned_pan)

    print("\n==== Running parse_amount ====")
    value = _safe_input("Enter an amount (e.g. Rs 12,50,000): ")
    amount = parse_amount(value)
    if amount is None:
        print("Amount in rupees: Invalid amount input")
    else:
        print("Amount in rupees:", amount)

    print("\n==== Running parse_tax_slab ====")
    value = _safe_input("Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): ")
    slab = parse_tax_slab(value)
    if slab is None:
        print("Tax slab (low, high, rate): Invalid tax slab input")
    else:
        print("Tax slab (low, high, rate):", slab)


if __name__ == "__main__":
    main()
