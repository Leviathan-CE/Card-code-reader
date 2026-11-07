from pathlib import Path

import pandas as pd
import pytest

from ccr import codec
from ccr import labels

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"


def test_project_datasets_are_found() -> None:
    files = labels.discover_label_files(DATASETS)
    names = {path.parent.name for path in files}
    assert names == {"HMIV MKI", "camera", "synthetic"}


def test_each_dataset_loads() -> None:
    loaded = {
        path.parent.name: labels.load_labels(path)
        for path in labels.discover_label_files(DATASETS)
    }

    synthetic = loaded["synthetic"].set_index("image")
    assert int(synthetic.loc["images/all_zero.png", "value"]) == 0
    assert int(synthetic.loc["images/all_ones.png", "value"]) == 4194303
    assert pd.isna(synthetic.loc["images/blank_card.png", "value"])
    assert synthetic.loc["images/blank_card.png", "bits"] == ""

    assert loaded["camera"].empty
    assert list(loaded["camera"].columns) == list(labels.COLUMNS)

    hmiv = loaded["HMIV MKI"]
    assert len(hmiv) == 7
    assert hmiv["value"].nunique(dropna=False) == 1
    assert hmiv["bits"].nunique(dropna=False) == 1
    for image_path in hmiv["image_path"]:
        assert image_path.is_file()


def test_bits_column_matches_mapper() -> None:
    for csv_path in labels.discover_label_files(DATASETS):
        frame = labels.load_labels(csv_path)
        for row in frame.itertuples(index=False):
            if pd.isna(row.value):
                continue
            if row.bits == "":
                continue
            assert codec.bits_to_int32(row.bits) == int(row.value)


def test_image_paths_stay_inside_their_dataset() -> None:
    for csv_path in labels.discover_label_files(DATASETS):
        frame = labels.load_labels(csv_path)
        for row in frame.itertuples(index=False):
            assert row.image_path == csv_path.parent / row.image


def _write_csv(directory: Path, body: str) -> Path:
    path = directory / "labels.csv"
    path.write_text(body, encoding="utf-8")
    return path


def test_comments_and_blank_lines_are_skipped(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                "# title",
                ",".join(labels.HEADER),
                "",
                "images/one.png,1,0000000000000000000001,first",
                "# ignored",
                "images/two.png,2,,second",
            ]
        )
        + "\n",
    )
    frame = labels.load_labels(path)
    assert list(frame["image"]) == [
        "images/one.png",
        "images/two.png",
    ]
    assert frame.iloc[1]["bits"] == ""
    assert int(frame.iloc[1]["value"]) == 2


def test_duplicate_image_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(labels.HEADER),
                "images/one.png,1,,",
                "images/one.png,2,,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="duplicate image"):
        labels.load_labels(path)


def test_bits_that_disagree_with_value_are_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(labels.HEADER),
                "images/one.png,1,0000000000000000000000,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="equal 0, not 1"):
        labels.load_labels(path)


def test_none_with_bits_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(labels.HEADER),
                "images/one.png,none,0000000000000000000000,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="none cannot include bits"):
        labels.load_labels(path)


def test_value_above_22_bits_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(labels.HEADER),
                "images/one.png,4194304,,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="0 through 4194303"):
        labels.load_labels(path)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        labels.load_labels(tmp_path / "missing.csv")
