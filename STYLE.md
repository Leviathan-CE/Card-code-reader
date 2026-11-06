# Style guide

This file is the layout and code style for the card-code reader. New batches and new Python follow it.

## Folders

```text
card-code-reader/
  LICENSE                 MIT, copyright Levi Boswell
  pyproject.toml          install name ccr
  PLAN.md
  STYLE.md
  src/ccr/                the library people import
    __init__.py           public names
    codec.py              22-bit string to int32, and back
    labels.py             read a labels.csv
  tests/
    test_codec.py
    test_labels.py
  datasets/
    synthetic/
      labels.csv
      images/
    kyber/
      labels.csv
      images/
    camera/
      labels.csv
      images/
  outputs/                decoder debug files, created when the scanner writes them
```

`datasets/` is labeled input. One batch is one folder. The batch name is lowercase. Use an underscore when the name needs two words, as in `walking_bit`.

Each batch contains:

- `labels.csv`, always that filename
- `images/`, always that folder name

`outputs/` is for crops, debug overlays, and failed reads. Generated files stay there. They are not added to a label sheet.

Python tests live in `tests/test_*.py`. They are code checks. They are not a place to store card photos.

## Adding a batch

1. Create `datasets/<name>/images/`.
2. Put the pictures in that `images/` folder.
3. Create `datasets/<name>/labels.csv` with the header below.
4. Add one row per picture.

A row names the file from the CSV's own folder:

```csv
image,value,bits,note
images/Kyber-II Optics.png,450577,0001101110000000010001,rendered card
```

`src/ccr/labels.py` joins that `image` cell onto the CSV's directory. A sheet in `datasets/kyber/` cannot point at `datasets/synthetic/images` with a short path. Write the path from the sheet's own folder.

`discover_label_files` finds `datasets/*/labels.csv` only. A CSV nested deeper than that is ignored. Keep one sheet per batch.

## Label sheet

UTF-8, comma-separated. The header row is required and is exactly:

```text
image,value,bits,note
```

A line whose first character is `#` is a comment. Blank lines are skipped. The same `image` path twice in one sheet is an error.

| Column | Required | Rule |
|---|---|---|
| `image` | yes | Path relative to the CSV, starting with `images/` |
| `value` | yes | Decimal integer from 0 through 4194303, or `none` |
| `bits` | no | 22 characters of `0` and `1`. When present, the integer of those bits equals `value` |
| `note` | no | Free text. The loader keeps it and the decoder ignores it |

`none` means the picture must return no read. That row leaves `bits` empty.

The leftmost bit has weight 2^21. Twenty-two ones equal 4194303. The Kyber bits `0001101110000000010001` equal 450577.

The loader checks the sheet before any picture is opened. A bad row stops the load. The image scanner does not live in `codec.py` or `labels.py`.

## Library

The install name and the import name are both `ccr`. The project folder can stay `card-code-reader`. `LICENSE` is the MIT license, copyright Levi Boswell, 2026. MIT lets other people use, change, and ship the code, including in closed-source work, as long as they keep that license notice.

People install the package and write:

```python
from ccr import bits_to_int32, load_labels
```

`src/ccr/__init__.py` lists the public names in `__all__`. A new public function is added there. A helper whose name starts with `_` stays inside its module.

`datasets/`, `tests/`, `PLAN.md`, and `STYLE.md` stay beside the package. They are not installed. The scanner, when it exists, is a module under `src/ccr/` and is exported from `__init__.py` once it can return an int32 from an image.

`pyproject.toml` is the package record: version `0.1.0`, Python 3.11 or newer, license `MIT`. Pytest uses `pythonpath = ["src"]`, so the tests import the package without a separate install step.

## Python

Match the style already in `src/ccr/codec.py` and `src/ccr/labels.py`.

- One job per module. `codec.py` maps bits and integers. `labels.py` reads sheets. The scanner, when it exists, reads images and calls the codec. Inside the package, import a sibling as `from ccr.codec import bits_to_int32`.
- Check the failing cases at the top of the function, then return the result. Keep the happy path at the bottom.
- Name a check after the condition it guards: empty path, wrong length, value out of range, duplicate image.
- A function that loads data raises `ValueError` or `FileNotFoundError` with the image path or file path in the message.
- Expected integers for pictures live in `labels.csv`. Tests read those rows. They do not copy the expected integer into the test body when the sheet already has it.
- Use `pathlib.Path` for files. Image paths in the CSV use forward slashes.

## Current batches

- `datasets/synthetic/` holds generated symbols. The image files for all-zero, all-ones, and the blank card are still to be added. The rows are already labeled.
- `datasets/HMIV MKI/` holds seven photos of one card at different orientations. Every row is value 335889 and bits `0001010010000000010001`.
- `datasets/camera/` is an empty sheet for photographs.
- `datasets/needs sorting/` is a holding folder. It has no `labels.csv`, so the loader skips it.
