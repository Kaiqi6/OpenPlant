# Reconstructing the published OpenPlant benchmark

The release manifest is the selection and split authority. The builder processes
exactly its rows. It does not rerun random sampling, invent missing samples, merge
classes, or alter the downloaded sources. No local source image collection was
examined to create this release's metadata: it is exported from the saved mapping
workbook. Empty checksum fields mean that original image byte identity has not
been established.

## 1. Obtain the source datasets

Use `metadata/sources.csv` and the source documentation to download the original
versions under their respective licenses. Unpack them into a separate source
directory. `source_image_path` is relative to this directory; it corresponds to
the old mapping workbook's `Original Path`, with its `download/` prefix removed.
Keep annotations as well as images. The script does not bypass access conditions
or substitute another dataset version.

Inspect a few manifest rows for the exact expected layout. For example, a record
with `source_image_path=PlantDoc-Dataset-master/train/Apple leaf/a.jpg` expects that
path under `--source-root`. If an archive introduces a different directory prefix,
declare the mapping explicitly:

```bash
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --alias "PlantDoc-Dataset-master=PlantDoc-Dataset-main"
```

Aliases change only how paths are resolved. They do not rename any file. Source
and output directories must be separate and neither may contain the other.

## 2. Validate metadata without accessing images

```bash
python scripts/validate_dataset.py --manifest metadata/manifest.csv.gz --classes metadata/classes.csv --summary metadata/summary.json --manifest-only
```

This checks the manifest schema, unique sample/output paths, class ID/name
consistency, fixed splits, every per-class/split count in `classes.csv`, totals and
manifest checksum in `summary.json`, and portable paths. It prints the SHA-256 of the
manifest file. Supply `--manifest-sha256 EXPECTED` to compare against an
independently recorded release checksum. This mode does not open source or output
images and does not certify their existence or byte identity.

## 3. Rebuild a small selection, then the release

```bash
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --limit 20
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --resume
python scripts/validate_dataset.py --output-root /data/openplant
```

For a single source, add `--source SOURCE_ID`, using the exact `source_id` from the
manifest. Repeat this option for multiple sources. `--limit` takes the first N
selected records in manifest order and is explicitly reported as a partial check.
It does not define a new benchmark subset.

The builder applies the published preprocessing: source image or annotated crop,
RGB conversion, short edge 256 with the other edge truncated to an integer while
preserving aspect ratio, PIL bilinear resizing, and PNG output. It does not apply
EXIF orientation corrections, normalization, augmentation, or center cropping;
those would change the historical preprocessing. Inference transforms belong in
the evaluation pipeline.

For copied-image sources, the curated image is the source file itself. For the
six detection sources below, the original adapters first saved a cropped JPEG
with Pillow defaults. The new builder reproduces that JPEG encoding/decoding
step before RGB resizing. Skipping this lossy intermediate would produce different
pixels. `curated_path` retains the historical curated name; `image_path` identifies
the final PNG in the frozen split/class folder.

`--resume` verifies an existing image against its manifest hash when available.
With an empty hash, it reconstructs the image again and compares byte hashes; it
does not silently accept an existing filename. Mismatches are never overwritten.
Missing sources, missing annotations, invalid records, unsupported recipes and
encoding/checksum mismatches produce errors and a nonzero exit status. A failed
run can leave already completed valid images; use `--resume` after fixing the
reported cause. `build_report.json` records counts, errors, split/source totals,
Pillow version and the number of records without source/output reference hashes.

## Annotation-grounded crops

The builder dynamically reads annotations from the user's source directory when
no exported recipe is supplied. It enumerates annotations and applies the original
adapter's acceptance rules, then matches the exact historical output name in the
manifest. Names select enumerated annotations; coordinates always come from
annotations and, for YOLO, the original image dimensions.

| Source | Required annotation layout relative to source root | Original rule preserved |
| --- | --- | --- |
| CottonWeedDet12 | `CottonWeedDet12/weedcoco.json` | COCO annotation ID; exclude categories 1 and 7; integer x/y/w/h; crop all remaining boxes |
| Weed25 | `Weed25/annatations/<annotation-folder>/<image-stem>.xml` | Original folder spelling aliases; Pascal VOC object order; both dimensions at least 128; aspect ratio 0.5–2 |
| WeedNet-R | `WeedNet-R/dataset/Annotations/<image-stem>.xml` | Only `crop` objects; float coordinates truncated to integers; size/aspect filter |
| VCD | Beside `DB_Mendeley/dataset/<image>` as `.xml`, otherwise `.json` | Only maize/bean/leek; XML preferred; JSON minima clamped to zero; size/aspect filter |
| ImageWeeds | `ImageWeeds/.../labels/TXT/<image-stem>.txt` | YOLO classes 0–3; size/aspect filter; seven explicit bad-crop exclusions; preserve accepted-object numbering; RGBA/P converted to RGB before JPEG |
| TobSet | `TobSet/labels_NN/<image-stem>.txt` for `tobacco_NN` images | YOLO class 0; pixel-coordinate conversion; size/aspect filter |

The original spelling `annatations` is intentional. No crop is inferred from an
image's appearance or a bounding-box-like filename. If the stored name cannot be
matched to an accepted original annotation, processing fails with the sample ID.
The historical VCD worksheet records only source basenames; its dedicated adapter
also resolves these under `DB_Mendeley/dataset`, as explicitly specified in the
original VCD script. This does not change manifest records or search arbitrary
directories for similarly named files.

After obtaining source files, users may export reusable crop recipes separately:

```bash
python tools/enrich_recipes.py --source-root /data/sources --output metadata/recipes.csv.gz
python scripts/build_dataset.py --source-root /data/sources --output-root /data/openplant --recipes metadata/recipes.csv.gz --resume
```

The exporter reads annotations and YOLO image dimensions. It does not write source
files or reconstruct images. The optional `--archive FILE.zip` reads explicitly
selected ZIP members without extraction; use `--alias EXPECTED=ACTUAL` for member
prefixes. It does not automatically open nested archives or make ambiguous basename
matches. Failed export does not publish an incomplete recipe table. Exported
recipes contain sample/recipe IDs, annotation path/SHA-256/ID, integer crop bounds,
JPEG encoding mode and recipe version. `--source` and `--limit` produce explicitly
partial exports. The builder checks an exported annotation's checksum against
the source annotation before using it.

## Known reconstruction limits

The saved workbook determines membership, labels and splits. It does not contain
all historical source-version identifiers, original file hashes, or crop
coordinates. Dynamic parsing verifies consistency with annotations that the user
provides; it cannot establish that those annotations are byte-identical to the
ones used for the paper when no historical checksum exists.

In particular, the old PlantDoc adapter renamed downloaded files before recording
their `Original Path`. A fresh download may therefore use different names. When a
verified `source_sha256` is available, `--index-source` searches downloaded images
by content without renaming them. With an empty source checksum, an absent renamed
file cannot be resolved safely from this workbook alone; the builder reports the
exact missing record. An author-provided original-to-curated mapping or source
hash list is required to remove that limitation. Directory aliases only solve
directory-layout differences, not lost original filenames.

An explicit per-file mapping can be supplied with `--path-map path_map.csv`:

```csv
source_id,source_image_path,downloaded_path
PlantDoc,PlantDoc-Dataset-master/train/Apple leaf/Apple_train_000.jpg,PlantDoc-Dataset-master/train/Apple leaf/original_filename.jpg
```

Both paths are relative to the source root. `source_image_path` must match the
manifest; `downloaded_path` is the verified corresponding file in the user's
download. The example is a schema illustration, not a claimed real correspondence.
Duplicate entries, unsafe paths, missing mapped files and supplied checksum
mismatches fail. Explicit mappings take precedence over directory aliases and
content indexing. This table is not bundled because the saved workbook does not
establish the original PlantDoc filenames. That source cannot be described as a
fully automatic fresh-download reconstruction without the additional table or
verified source hashes.

Checksums in this metadata release are optional and may be blank. Output validation
then checks readable RGB PNGs, dimensions, expected files, counts, labels/splits,
and unexpected extra images. Its `byte_identity_verified` flag remains false.
Use `--require-hashes` only with a release that includes verified per-image hashes.
Pillow/libjpeg/zlib version differences can also change encoded bytes; when hashes
are present, the builder detects this rather than calling the output identical.
For an independent audit, retain the report, exact dependency versions, source
archive versions/checksums, and any recipe table used.

The frozen manifest reproduces the historical split; it does not establish an
absence of duplicate images or parent-image overlap across splits. Any revised
deduplication or group-aware split should be released as a separately versioned
benchmark instead of silently replacing this one.

## Development checks

```bash
python -m unittest discover -s tests -p test_rebuild.py -v
```

These tests use temporary synthetic images and annotations. They cover frozen
selection, all six crop formats, the JPEG intermediate, strict resume, content
matching, aliases, metadata/output validation, duplicate/path safety, and error
reporting. They do not inspect or modify an author's local dataset.
