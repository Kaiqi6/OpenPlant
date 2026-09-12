"""Export fixed paper membership from Excel without accessing any image files."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath

FIELDS = ["sample_id", "source_id", "source_image_path", "class_id", "class_name",
          "split", "curated_path", "image_path", "source_sha256", "curated_sha256",
          "image_sha256", "recipe_id", "image_bytes", "width", "height"]
CROP_SOURCES = {"Weed25", "CottonWeedDet12", "WeedNet-R", "VCD", "ImageWeeds", "TobSet"}


def relative_path(value, prefix):
    value = str(value).replace("\\", "/")
    if value.startswith(prefix + "/"):
        value = value[len(prefix) + 1:]
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ":" in value:
        raise ValueError(f"Unsafe historical path: {value}")
    return path.as_posix()


def file_digest(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class GzipText:
    """Deterministic gzip writer; closes both wrapper and underlying file."""
    def __init__(self, path):
        self.raw = open(path, "wb")
        self.text = io.TextIOWrapper(gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0), encoding="utf-8", newline="")

    def __enter__(self):
        return self.text

    def __exit__(self, *exc):
        self.text.close()
        self.raw.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("metadata"))
    args = parser.parse_args()
    import openpyxl
    args.output_dir.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.load_workbook(args.workbook, read_only=True, data_only=True)
    summary = list(workbook["datasets"].values)
    names = sorted(str(row[0]) for row in summary[1:] if row[0])
    if len(set(names)) != len(names):
        raise ValueError("Duplicate class names in workbook summary")
    expected = {row[0]: row[-1] for row in summary[1:] if row[0]}
    class_ids = {name: i for i, name in enumerate(names)}
    source_counts, split_counts = Counter(), Counter()
    class_counts, source_splits = defaultdict(Counter), defaultdict(Counter)
    seen_paths, seen_ids, examples = set(), set(), []
    count = 0
    temporary = args.output_dir / "manifest.csv.gz.tmp"
    with GzipText(temporary) as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for sheet in workbook:
            if sheet.title == "datasets":
                continue
            if list(next(sheet.values)[:4]) != ["Class Name", "Original Path", "New Path", "Subset"]:
                raise ValueError(f"Unexpected columns in {sheet.title}")
            for value in sheet.iter_rows(min_row=2, values_only=True):
                if not any(v is not None for v in value):
                    continue
                name, original, new, split = value[:4]
                if name not in class_ids or split not in {"train", "val", "test"}:
                    raise ValueError(f"Invalid record: {sheet.title} {value}")
                curated = relative_path(new, "Mydatasets")
                image_path = str(PurePosixPath(curated).with_suffix(".png"))
                if PurePosixPath(image_path).parts[:2] != (split, name):
                    raise ValueError(f"Path / label / split mismatch: {value}")
                sample_id = "op_" + hashlib.sha256((sheet.title + "\0" + curated).encode("utf-8")).hexdigest()[:24]
                if image_path.casefold() in seen_paths or sample_id in seen_ids:
                    raise ValueError(f"Duplicate output path / ID: {image_path}")
                seen_paths.add(image_path.casefold())
                seen_ids.add(sample_id)
                row = dict.fromkeys(FIELDS, "")
                row.update(sample_id=sample_id, source_id=sheet.title,
                           source_image_path=relative_path(original, "download"),
                           class_id=class_ids[name], class_name=name, split=split,
                           curated_path=curated, image_path=image_path,
                           recipe_id=sample_id if sheet.title in CROP_SOURCES else "rgb_resize256_png_v1")
                writer.writerow(row)
                if source_counts[sheet.title] < 2:
                    examples.append(row)
                count += 1
                source_counts[sheet.title] += 1
                split_counts[split] += 1
                source_splits[sheet.title][split] += 1
                class_counts[name][split] += 1
            print(f"{sheet.title}: {source_counts[sheet.title]:,} records", flush=True)
    workbook.close()
    for name in names:
        if sum(class_counts[name].values()) != expected[name]:
            raise ValueError(f"Summary / record count mismatch for {name}")
    if count != 635176 or len(names) != 1167:
        raise ValueError(f"Unexpected benchmark size: {count} images / {len(names)} classes")
    os.replace(temporary, args.output_dir / "manifest.csv.gz")
    with (args.output_dir / "classes.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["class_id", "class_name", "train_count", "val_count", "test_count", "total_count"])
        for name in names:
            counter = class_counts[name]
            writer.writerow([class_ids[name], name, counter["train"], counter["val"], counter["test"], sum(counter.values())])
    with (args.output_dir / "manifest_examples.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(examples)
    with (args.output_dir / "source_counts.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_id", "train_count", "val_count", "test_count", "total_count"])
        for source in sorted(source_counts):
            counter = source_splits[source]
            writer.writerow([source, counter["train"], counter["val"], counter["test"], source_counts[source]])
    report = {
        "release": "OpenPlant paper benchmark", "paper_doi": "10.3390/plants15050727",
        "workbook_filename": args.workbook.name, "workbook_sha256": file_digest(args.workbook),
        "samples": count, "classes": len(names), "source_groups": len(source_counts),
        "splits": dict(split_counts), "sources": dict(source_counts),
        "manifest_sha256": file_digest(args.output_dir / "manifest.csv.gz"),
        "class_order": "Python sorted class names; torchvision ImageFolder order",
        "manifest_basis": "Historical workbook records; no image files read or modified during export",
        "image_verification": "Not performed; per-image checksum, size and dimension fields are empty",
        "preprocessing": {"mode": "RGB", "short_edge": 256, "resize": "bilinear", "format": "PNG"},
    }
    (args.output_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
