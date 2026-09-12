# Image manifest and class vocabulary

The paper benchmark is defined by `metadata/manifest.csv.gz`, a UTF-8, comma-separated table containing 635,176 records. Gzip compression keeps the complete list convenient to download from GitHub. `manifest_examples.csv` is an excerpt; it is not a training subset.

## Fields

| Column | Meaning |
|---|---|
| `sample_id` | Stable release ID: `op_` plus the first 24 hexadecimal characters of SHA-256 over `source_id + NUL + curated_path` (UTF-8). This identifies a record, not image content. |
| `source_id` | Exact source worksheet name; join to `sources.csv` and `source_counts.csv`. |
| `source_image_path` | Historical `Original Path`, with separators normalized to `/` and a leading `download/` removed where present. Some source paths are filenames only; consult the source-root guide. |
| `class_id` | Zero-based integer from the ordered `classes.csv`. |
| `class_name` | Historical unified label, retained verbatim to preserve benchmark identity. |
| `split` | Fixed assignment: `train`, `val`, or `test`. |
| `curated_path` | Historical `New Path`, relative to the curated dataset root (`Mydatasets/` prefix removed). |
| `image_path` | Prepared path under the output root: same split/class/basename as `curated_path`, with `.png` extension. |
| `recipe_id` | `rgb_resize256_png_v1` for copied source images, or the sample ID for an object-crop recipe. Recipes are derived from the downloaded source annotations during reconstruction. |
| `source_sha256` | Optional original-image byte hash. Empty in this release because the workbook does not contain it. |
| `curated_sha256` | Optional intermediate curated-image byte hash. Empty in this release. |
| `image_sha256` | Optional final PNG byte hash. Empty in this release. |
| `image_bytes`, `width`, `height` | Optional final-file metadata. Empty in this release. |

Empty values mean unavailable, not zero. Record IDs must never be used as image hashes. The workbook identifies selected samples and partitions, but it does not supply all upstream filenames, crop coordinates, or image checksums.

## Counts and class order

`classes.csv` uses Python's lexicographic sorting of the 1,167 exact class names, matching torchvision ImageFolder's class indexing. It includes training, validation, test, and total counts. Keep the original spelling and capitalization when using published checkpoints; a taxonomic spelling update belongs in a separately versioned mapping.

`source_counts.csv` counts derived classification samples, which can include several object crops from a single photograph. A source-photo count and an OpenPlant-sample count are different quantities. The same unified class may appear in multiple sources, so source-level class counts cannot be added together.

The fixed split contains 443,996 training, 63,224 validation, and 127,956 test records. These are the recorded assignments, including source-specific rounding; they are not recomputed from the nominal 7:1:2 ratio.

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

The source is the historical `image_mapping_test_0220.xlsx` workbook. Its SHA-256 and the compressed manifest checksum are recorded in `summary.json`. The exporter checks every record's path/label/split consistency, output-path and ID uniqueness, class totals against the workbook summary, and the overall 635,176 / 1,167 counts.

To regenerate metadata from that workbook, install `openpyxl` and run:

```bash
python tools/export_paper_manifest.py --workbook /path/to/image_mapping_test_0220.xlsx --output-dir metadata
```

This utility reads only the mapping workbook. It never reads, resizes, moves, renames, or deletes image files. Exported image membership was not compared with local image folders during the final release export. Run the validator against a reconstructed copy to check its structure and image readability; byte identity requires independently supplied hashes.

Preserve this manifest for comparisons with the published paper. Additions, removals, corrected labels, or changed splits should be released with a new manifest and version rather than silently replacing the paper benchmark.
