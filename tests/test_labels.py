from pathlib import Path

import pytest

from ccr import HEADER, bits_to_int32, discover_label_files, load_labels

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"


def test_project_datasets_are_found() -> None:
    files = discover_label_files(DATASETS)
    names = {path.parent.name for path in files}
    assert names == {"HMIV MKI", "camera", "synthetic"}


def test_each_dataset_loads() -> None:
    loaded = {path.parent.name: load_labels(path) for path in discover_label_files(DATASETS)}

    synthetic = {label.image: label for label in loaded["synthetic"]}
    assert synthetic["images/all_zero.png"].value == 0
    assert synthetic["images/all_ones.png"].value == 4194303
    assert synthetic["images/blank_card.png"].value is None
    assert synthetic["images/blank_card.png"].bits == ""

    assert loaded["camera"] == []

    hmiv = loaded["HMIV MKI"]
    assert len(hmiv) == 7
    assert len({label.value for label in hmiv}) == 1
    assert len({label.bits for label in hmiv}) == 1
    for label in hmiv:
        assert label.image_path.is_file()


def test_bits_column_matches_mapper() -> None:
    for csv_path in discover_label_files(DATASETS):
        for label in load_labels(csv_path):
            if label.value is None:
                continue
            if label.bits == "":
                continue
            assert bits_to_int32(label.bits) == label.value


def test_image_paths_stay_inside_their_dataset() -> None:
    for csv_path in discover_label_files(DATASETS):
        for label in load_labels(csv_path):
            assert label.image_path == csv_path.parent / label.image


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
                ",".join(HEADER),
                "",
                "images/one.png,1,0000000000000000000001,first",
                "# ignored",
                "images/two.png,2,,second",
            ]
        )
        + "\n",
    )
    labels = load_labels(path)
    assert [label.image for label in labels] == ["images/one.png", "images/two.png"]
    assert labels[1].bits == ""
    assert labels[1].value == 2


def test_duplicate_image_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(HEADER),
                "images/one.png,1,,",
                "images/one.png,2,,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="duplicate image"):
        load_labels(path)


def test_bits_that_disagree_with_value_are_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(HEADER),
                "images/one.png,1,0000000000000000000000,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="equal 0, not 1"):
        load_labels(path)


def test_none_with_bits_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(HEADER),
                "images/one.png,none,0000000000000000000000,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="none cannot include bits"):
        load_labels(path)


def test_value_above_22_bits_is_rejected(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "\n".join(
            [
                ",".join(HEADER),
                "images/one.png,4194304,,",
            ]
        )
        + "\n",
    )
    with pytest.raises(ValueError, match="0 through 4194303"):
        load_labels(path)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_labels(tmp_path / "missing.csv")
