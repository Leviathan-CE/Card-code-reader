import pytest

from ccr import MAX_VALUE, bits_to_int32, int32_to_bits

KYBER_BITS = "0001101110000000010001"
KYBER_VALUE = 450577


def test_zero_and_all_ones() -> None:
    assert bits_to_int32("0" * 22) == 0
    assert bits_to_int32("1" * 22) == MAX_VALUE
    assert MAX_VALUE == 4194303


def test_kyber_sample() -> None:
    assert bits_to_int32(KYBER_BITS) == KYBER_VALUE


def test_roundtrip() -> None:
    for value in (0, 1, KYBER_VALUE, MAX_VALUE):
        assert bits_to_int32(int32_to_bits(value)) == value


def test_leftmost_bit_is_highest_weight() -> None:
    bits = "1" + ("0" * 21)
    assert bits_to_int32(bits) == 2**21


def test_rejects_bad_bits() -> None:
    with pytest.raises(ValueError):
        bits_to_int32("0" * 21)
    with pytest.raises(ValueError):
        bits_to_int32("0" * 23)
    with pytest.raises(ValueError):
        bits_to_int32("0000000000000000000002")


def test_rejects_value_outside_22_bits() -> None:
    with pytest.raises(ValueError):
        int32_to_bits(-1)
    with pytest.raises(ValueError):
        int32_to_bits(MAX_VALUE + 1)
