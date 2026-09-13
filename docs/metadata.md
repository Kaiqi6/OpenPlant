# Image manifest and class vocabulary

[`manifest.csv.gz`](../metadata/manifest.csv.gz) is the paper benchmark's UTF-8 CSV
of 635,176 selected samples. `manifest_examples.csv` illustrates its format.
For obtaining the images, see [Reconstruction](reconstruction.md) and
[Data licensing](../DATA_LICENSE.md).

## Fields

| Column | Meaning |
|---|---|
| `sample_id` | Record ID: `op_` plus the first 24 hexadecimal characters of SHA-256 over `source_id + NUL + curated_path` (UTF-8). |
| `source_id` | Exact source worksheet name; join to `sources.csv` and `source_counts.csv`. |
| `source_image_path` | Historical `Original Path`, with `/` separators and a leading `download/` removed. See [source layouts](reconstruction.md#annotation-grounded-crops) for filename-only records. |
| `class_id` | Zero-based integer from the ordered `classes.csv`. |
| `class_name` | Historical unified label, retained verbatim. |
| `split` | Fixed assignment: `train`, `val`, or `test`. |
| `curated_path` | Historical `New Path`, relative to the curated dataset root (`Mydatasets/` prefix removed). |
| `image_path` | Output path: `curated_path` with the extension changed to `.png`. |
| `recipe_id` | `rgb_resize256_png_v1` for copied images; sample ID for crops derived from source annotations. |
| `source_sha256` | Optional source-image byte hash. |
| `curated_sha256` | Optional intermediate-image byte hash. |
| `image_sha256` | Optional output PNG byte hash. |
| `image_bytes`, `width`, `height` | Optional output file size in bytes and dimensions in pixels. |

The hash, size and dimension fields are empty in this release; empty means
unavailable. `sample_id` identifies a record and cannot verify image bytes.

## Counts and class order

`classes.csv` sorts the 1,167 class names lexicographically, matching torchvision
ImageFolder indices. It includes counts for each split and their total. Preserve
spelling and capitalization when using published checkpoints.

`source_counts.csv` counts classification samples; one photograph may yield several
crops. Classes can appear in multiple sources, so source-level class counts cannot
be summed to obtain the benchmark's class count.

The recorded split is **443,996 train / 63,224 val / 127,956 test**, including
source-specific rounding. Reconstruction uses these assignments directly.

## Reading the list

```python
import csv
import gzip

with gzip.open("metadata/manifest.csv.gz", "rt", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if row["split"] == "test" and row["source_id"] == "PlantVillage":
            print(row["sample_id"], row["image_path"], row["class_name"])
```

## Provenance and versioning

The manifest comes from `image_mapping_test_0220.xlsx`. `summary.json` records the
workbook and compressed-manifest checksums. Validate IDs, paths, class/split counts
and these release totals with:

```bash
python scripts/validate_dataset.py --classes metadata/classes.csv --summary metadata/summary.json --manifest-only
```

To regenerate metadata from that workbook, install `openpyxl` and run:

```bash
python tools/export_paper_manifest.py --workbook /path/to/image_mapping_test_0220.xlsx --output-dir metadata
```

Export reads the workbook. Image reconstruction and verification are covered in
the [build guide](reconstruction.md). Publish sample, label or split changes as a
new version, keeping this manifest available for paper comparisons.
