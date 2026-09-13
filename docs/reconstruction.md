# Reconstructing the published OpenPlant benchmark

The complete image collection is not distributed at present because some source
licenses may restrict redistribution of original or modified images. Obtain the
images from their original providers under the applicable licenses, then follow
the local build steps below. See [Data licensing](../DATA_LICENSE.md) for details.

The manifest fixes the selected samples, labels and splits. The builder processes
those records using downloaded source images and annotations.

## 1. Obtain the source datasets

Download the versions listed in [`sources.csv`](../metadata/sources.csv), including
annotations for detection datasets. Unpack them under `--source-root` using the
manifest's `source_image_path` layout. For a different archive directory name,
supply a prefix alias:

```bash
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --alias "PlantDoc-Dataset-master=PlantDoc-Dataset-main"
```

Aliases resolve directory names without renaming files. Source and output roots
must be separate; neither may contain the other. Paths must stay within their
respective roots. See [Known reconstruction limits](#known-reconstruction-limits)
for individual filename mappings.

## 2. Validate metadata without accessing images

```bash
python scripts/validate_dataset.py --manifest metadata/manifest.csv.gz --classes metadata/classes.csv --summary metadata/summary.json --manifest-only
```

This checks unique IDs and paths, class indexing, fixed splits, per-class counts,
and the totals and manifest checksum in `summary.json`. It accesses metadata only.
Use `--manifest-sha256 EXPECTED` to check an independently recorded checksum.

## 3. Rebuild a small selection, then the release

```bash
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --limit 20
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --resume
python scripts/validate_dataset.py --output-root /data/openplant
```

Add `--source SOURCE_ID` to select a source; repeat for several sources. `--limit N`
processes the first N selected manifest rows and reports a partial run.

Preprocessing converts the source image or crop to RGB, resizes its short edge to
256 with PIL bilinear interpolation, and saves a PNG. The longer edge is truncated
to an integer. Detection crops first pass through JPEG encoding and decoding with
Pillow defaults, as in the original adapters. EXIF rotation, augmentation and
normalization are outside this preparation step.

`--resume` checks existing output against the manifest hash, or against newly
reconstructed bytes when the hash is empty. Mismatches are left untouched.
Missing files, invalid annotations and checksum errors return a nonzero exit
status. Fix the reported cause and resume; completed images are retained.
`build_report.json` records counts, errors, dependency version and hash coverage.

## Annotation-grounded crops

By default, the builder reads source annotations, applies the original acceptance
rules and matches each crop's historical name to the manifest. Coordinates come
from annotations and, for YOLO, the source image dimensions. The size/aspect filter
below requires both dimensions to be at least 128 pixels and a width/height ratio
of 0.5–2.

| Source | Required annotation layout relative to source root | Original rule preserved |
| --- | --- | --- |
| CottonWeedDet12 | `CottonWeedDet12/weedcoco.json` | COCO annotation ID; exclude categories 1 and 7; integer x/y/w/h; crop all remaining boxes |
| Weed25 | `Weed25/annatations/<annotation-folder>/<image-stem>.xml` | Original folder aliases; Pascal VOC object order; size/aspect filter |
| WeedNet-R | `WeedNet-R/dataset/Annotations/<image-stem>.xml` | Only `crop` objects; float coordinates truncated to integers; size/aspect filter |
| VCD | Beside `DB_Mendeley/dataset/<image>` as `.xml`, otherwise `.json` | Only maize/bean/leek; XML preferred; JSON minima clamped to zero; size/aspect filter |
| ImageWeeds | `ImageWeeds/.../labels/TXT/<image-stem>.txt` | YOLO classes 0–3; size/aspect filter; seven explicit bad-crop exclusions; preserve accepted-object numbering; RGBA/P converted to RGB before JPEG |
| TobSet | `TobSet/labels_NN/<image-stem>.txt` for `tobacco_NN` images | YOLO class 0; pixel-coordinate conversion; size/aspect filter |

The spelling `annatations` is intentional. VCD records contain source basenames;
the adapter resolves them under `DB_Mendeley/dataset`. An unmatched crop produces
an error identifying the sample.

To save reusable crop recipes:

```bash
python tools/enrich_recipes.py --source-root /data/sources --output metadata/recipes.csv.gz
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --recipes metadata/recipes.csv.gz --resume
```

Recipes record sample IDs, annotation paths/IDs/checksums, crop bounds and encoding
rules. The builder checks annotation checksums before use. The exporter can read
explicit ZIPs with `--archive FILE.zip` and prefix aliases with
`--alias EXPECTED=ACTUAL`; nested archives require separate extraction. An export error
leaves no partial table. `--source` and `--limit` also apply to recipe exports.

## Known reconstruction limits

The original PlantDoc adapter renamed files before recording their paths. A fresh
download may therefore need an original-to-recorded filename table. Supply verified
correspondences with `--path-map path_map.csv`, using this schema:

```csv
source_id,source_image_path,downloaded_path
PlantDoc,PlantDoc-Dataset-master/train/Apple leaf/Apple_train_000.jpg,PlantDoc-Dataset-master/train/Apple leaf/original_filename.jpg
```

The example illustrates the schema. Both paths are relative to `--source-root`;
`source_image_path` must match the manifest. Explicit mappings take precedence
over aliases. Duplicate entries, unsafe paths and missing targets fail. The
workbook lacks the original PlantDoc filenames, so a correspondence table is not
bundled. Automatic reconstruction of renamed files requires that table or verified
`source_sha256` values for content matching with `--index-source`.

This release has no per-image checksums. Output validation checks readable RGB
PNGs, dimensions, manifest membership and extra images; `byte_identity_verified`
remains false. Reference hashes are needed for paper-version byte comparisons;
use `--require-hashes` when they are available. Keep source versions, recipe tables
and dependency versions with the build report, since changed annotations or image
encoders can change the output.

The manifest preserves the recorded split. Any new deduplication, label corrections
or split rules should receive a separate benchmark version.

## Development checks

```bash
python -m unittest discover -s tests -p test_rebuild.py -v
```

Tests use synthetic images and annotations.
