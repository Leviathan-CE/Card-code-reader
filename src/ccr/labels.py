"""Load card label sheets.

Each row ties one image path to one int32.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from ccr import codec

HEADER = ("image", "value", "bits", "note")


@dataclass(frozen=True)
class Label:
    """One labeled image and the int32 it must decode to."""

    image: str
    image_path: Path
    value: int | None
    bits: str
    note: str


def discover_label_files(datasets_dir: str | Path) -> list[Path]:
    """Return each batch sheet directly under a datasets folder.

    Args:
        datasets_dir: Folder whose children are batches. A batch is
            included when it contains labels.csv.

    Returns:
        The labels.csv path for each batch that has one.

    Raises:
        FileNotFoundError: datasets_dir is not a folder.
    """
    root = Path(datasets_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"datasets folder not found: {root}")
    return sorted(root.glob("*/labels.csv"))


def load_labels(csv_path: str | Path) -> list[Label]:
    """Load one label sheet and check each row.

    Args:
        csv_path: Path to a labels.csv file.

    Returns:
        One Label per data row. Image paths are relative to the sheet.

    Raises:
        FileNotFoundError: csv_path is not a file.
        ValueError: The header, a value, the bits, or a repeated image
            path is invalid.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"label file not found: {path}")

    lines = _data_lines(path)
    if not lines:
        raise ValueError(f"{path}: label file has no header")

    reader = csv.DictReader(lines)
    if reader.fieldnames is None:
        raise ValueError(f"{path}: label file has no header")

    fieldnames = tuple(name.strip() for name in reader.fieldnames)
    if fieldnames != HEADER:
        joined = ",".join(HEADER)
        raise ValueError(f"{path}: header must be {joined}")

    labels: list[Label] = []
    seen: set[str] = set()
    for row in reader:
        label = _parse_row(row, path.parent)
        if label.image in seen:
            raise ValueError(f"{label.image}: duplicate image")
        seen.add(label.image)
        labels.append(label)
    return labels


def _data_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith("#"):
            continue
        lines.append(line)
    return lines


def _parse_row(row: dict[str, str | None], csv_dir: Path) -> Label:
    image = _cell(row, "image")
    if image == "":
        raise ValueError("image path is empty")

    value = _parse_value(image, _cell(row, "value"))
    bits = _parse_bits(image, _cell(row, "bits"), value)
    note = _cell(row, "note")
    return Label(
        image=image,
        image_path=csv_dir / image,
        value=value,
        bits=bits,
        note=note,
    )


def _cell(row: dict[str, str | None], name: str) -> str:
    raw = row.get(name)
    if raw is None:
        return ""
    return raw.strip()


def _parse_value(image: str, raw: str) -> int | None:
    if raw == "":
        raise ValueError(f"{image}: value is empty")
    if raw.lower() == "none":
        return None
    if not raw.isdigit():
        raise ValueError(f"{image}: value must be a decimal int32 or none")
    value = int(raw)
    if value > codec.MAX_VALUE:
        raise ValueError(
            f"{image}: value must be from 0 through {codec.MAX_VALUE}"
        )
    return value


def _parse_bits(image: str, bits: str, value: int | None) -> str:
    if value is None:
        if bits != "":
            raise ValueError(f"{image}: none cannot include bits")
        return ""
    if bits == "":
        return ""
    if len(bits) != codec.BIT_COUNT:
        raise ValueError(
            f"{image}: bits must be {codec.BIT_COUNT} characters"
        )
    parsed = codec.bits_to_int32(bits)
    if parsed != value:
        raise ValueError(
            f"{image}: bits {bits} equal {parsed}, not {value}"
        )
    return bits
