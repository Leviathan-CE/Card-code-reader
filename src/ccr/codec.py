"""Map a 22-bit card code to an int32. The leftmost bit has weight 2^21."""

BIT_COUNT = 22
MAX_VALUE = (1 << BIT_COUNT) - 1


def bits_to_int32(bits: str) -> int:
    if not isinstance(bits, str):
        raise TypeError("bits must be a string of 0 and 1")
    if len(bits) != BIT_COUNT:
        raise ValueError(f"bits must be {BIT_COUNT} characters, got {len(bits)}")
    if any(character not in "01" for character in bits):
        raise ValueError("bits must contain only 0 and 1")
    return int(bits, 2)


def int32_to_bits(value: int) -> str:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("value must be an int")
    if value < 0 or value > MAX_VALUE:
        raise ValueError(f"value must be from 0 through {MAX_VALUE}")
    return format(value, f"0{BIT_COUNT}b")
