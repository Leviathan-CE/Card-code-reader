"""Read a 22-bit card code as an int32."""

from ccr import codec
from ccr import labels

BIT_COUNT = codec.BIT_COUNT
MAX_VALUE = codec.MAX_VALUE
bits_to_int32 = codec.bits_to_int32
int32_to_bits = codec.int32_to_bits

COLUMNS = labels.COLUMNS
HEADER = labels.HEADER
Label = labels.Label
discover_label_files = labels.discover_label_files
load_labels = labels.load_labels

__all__ = [
    "BIT_COUNT",
    "COLUMNS",
    "HEADER",
    "MAX_VALUE",
    "Label",
    "bits_to_int32",
    "discover_label_files",
    "int32_to_bits",
    "load_labels",
]
