"""IPv4 address validation utilities."""


def is_valid_ipv4(address: str) -> bool:
    """Return True if `address` is a valid dotted-decimal IPv4 address.

    A valid IPv4 address consists of exactly four decimal octets separated by
    single dots. Each octet must be a decimal number in the inclusive range
    0-255, with no leading zeros (except the single-digit "0" itself) and no
    surrounding whitespace.

    Args:
        address: The string to validate.

    Returns:
        True if the string is a valid IPv4 address, False otherwise.
    """
    if not isinstance(address, str):
        return False

    octets = address.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        if not octet.isdigit():
            return False
        # Reject leading zeros (e.g. "01", "007") but allow "0".
        if len(octet) > 1 and octet[0] == "0":
            return False
        value = int(octet)
        if value < 0 or value > 255:
            return False

    return True
