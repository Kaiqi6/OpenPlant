"""Validate manifest structure and reconstructed OpenPlant output against it."""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

from .rebuild import IMAGE_EXTENSIONS, atomic_write, manifest_statistics, selected_rows, verify_digest
from .recipes import ReconstructionError, csv_rows, safe_join, sha256_file


def check_classes(path, stats):
    """Compare the full class index and every class/split count to the manifest."""
    found = set()
    for row in csv_rows(path):
        required = {"class_id", "class_name", "train_count", "val_count", "test_count", "total_count"}
        if not required.issubset(row):
            raise ReconstructionError("classes.csv is missing class identifiers/count columns")
        class_id = row["class_id"]
        if class_id in found or class_id not in stats["classes"]:
            raise ReconstructionError(f"Duplicate/unknown class_id in classes.csv: {class_id}")
        found.add(class_id)
        if row["class_name"] != stats["classes"][class_id]:
            raise ReconstructionError(f"Class name mismatch for class_id {class_id}")
        total = 0
        for split in ("train", "val", "test"):
            count = stats["class_splits"][(class_id, split)]
            if int(row[f"{split}_count"]) != count:
                raise ReconstructionError(f"classes.csv count mismatch: class_id {class_id}, split {split}")
            total += count
        if int(row["total_count"]) != total:
            raise ReconstructionError(f"classes.csv total_count mismatch: class_id {class_id}")
    if found != stats["classes"].keys():
        raise ReconstructionError("classes.csv does not cover every manifest class")
    # The released classifier indices follow torchvision.ImageFolder ordering.
    expected_order = {str(index): name for index, name in enumerate(sorted(stats["classes"].values()))}
    if stats["classes"] != expected_order:
        raise ReconstructionError("Class IDs do not match sorted ImageFolder class order")


def check_summary(path, stats, digest):
    with open(path, encoding="utf-8-sig") as stream:
        summary = json.load(stream)
    expected = {"samples": stats["samples"], "classes": len(stats["classes"]),
                "source_groups": len(stats["sources"]), "splits": dict(stats["splits"]),
                "sources": dict(stats["sources"]), "manifest_sha256": digest}
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReconstructionError(f"summary.json {key} does not match the manifest")


def validate(manifest, output_root=None, *, sources=(), limit=None, manifest_sha256=None,
             expected_samples=None, expected_classes=None, require_hashes=False,
             check_extras=True, max_errors=100, classes_path=None, summary_path=None):
    if limit is not None and limit <= 0:
        raise ReconstructionError("--limit must be positive")
    if max_errors <= 0:
        raise ReconstructionError("--max-errors must be positive")
    digest = sha256_file(manifest)
    if manifest_sha256:
        verify_digest(digest, manifest_sha256, "Manifest")
    stats = manifest_statistics(manifest, sources, limit, collect_paths=bool(output_root and check_extras and limit is None))
    if expected_samples is not None and stats["samples"] != expected_samples:
        raise ReconstructionError(f"Manifest has {stats['samples']} samples; expected {expected_samples}")
    if expected_classes is not None and len(stats["classes"]) != expected_classes:
        raise ReconstructionError(f"Manifest has {len(stats['classes'])} classes; expected {expected_classes}")
    if classes_path:
        check_classes(classes_path, stats)
    if summary_path:
        check_summary(summary_path, stats, digest)
    report = {"manifest_sha256": digest, "manifest_samples": stats["samples"],
              "manifest_classes": len(stats["classes"]), "selected": stats["selected"],
              "partial": bool(sources or limit), "mode": "output" if output_root else "manifest_only",
              "by_split": dict(stats["selected_splits"]),
              "by_source": dict(stats["selected_sources"]),
              "by_class": dict(stats["selected_classes"]),
              "checked_files": 0, "hash_verified_files": 0, "missing_image_hashes": 0,
              "unexpected_images": [], "errors": []}
    output = Path(output_root).resolve() if output_root is not None else None
    if output is not None and not output.is_dir():
        raise ReconstructionError(f"Output root does not exist: {output}")
    for position, row in enumerate(selected_rows(manifest, sources, limit), 1):
        try:
            expected_hash = row.get("image_sha256", "")
            if not expected_hash:
                report["missing_image_hashes"] += 1
                if require_hashes:
                    raise ReconstructionError("image_sha256 is empty; paper-version byte identity cannot be checked")
            if output is None:
                continue
            path = safe_join(output, row["image_path"])
            if not path.is_file():
                raise ReconstructionError(f"Missing output: {row['image_path']}")
            if expected_hash:
                verify_digest(sha256_file(path), expected_hash, "Output PNG")
                report["hash_verified_files"] += 1
            if row.get("image_bytes") and path.stat().st_size != int(row["image_bytes"]):
                raise ReconstructionError("Output byte length does not match manifest")
            with Image.open(path) as image:
                if image.format != "PNG" or image.mode != "RGB" or min(image.size) != 256:
                    raise ReconstructionError(f"Expected RGB PNG with short edge 256; got {image.format}/{image.mode}/{image.size}")
                image.load()  # Catch truncated pixel data, beyond merely opening a header.
            report["checked_files"] += 1
        except (OSError, ValueError, KeyError, Image.DecompressionBombError) as exc:
            report["errors"].append({"sample_id": row["sample_id"], "message": str(exc)})
            if len(report["errors"]) >= max_errors:
                report["stopped_early"] = position < stats["selected"]
                break
    if output is not None and check_extras and limit is None:
        known = stats["paths"]
        extra_count = 0
        for directory, dirs, files in os.walk(output, followlinks=False):
            for name in list(dirs):
                if Path(directory, name).is_symlink():
                    dirs.remove(name)
                    report["errors"].append({"message": f"Symlink directory cannot be audited: {Path(directory, name).relative_to(output).as_posix()}"})
            for name in files:
                path = Path(directory, name)
                if path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                relative = path.relative_to(output).as_posix()
                if relative not in known:
                    extra_count += 1
                    if len(report["unexpected_images"]) < max_errors:
                        report["unexpected_images"].append(relative)
        report["unexpected_image_count"] = extra_count
    else:
        report["extras_check"] = "not_requested" if not check_extras else "skipped_for_smoke_limit_or_manifest_only"
    report["ok"] = not report["errors"] and not report.get("unexpected_image_count", 0)
    report["byte_identity_verified"] = bool(output is not None and report["ok"]
                                            and report["hash_verified_files"] == stats["selected"])
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "metadata/manifest.csv.gz")
    parser.add_argument("--output-root", type=Path, help="Omit for metadata-only validation; no image files are accessed")
    parser.add_argument("--manifest-only", action="store_true", help="Validate metadata only; incompatible with --output-root")
    parser.add_argument("--classes", type=Path, help="Compare class index/order and per-class split counts")
    parser.add_argument("--summary", type=Path, help="Compare release counts and manifest hash")
    parser.add_argument("--source", action="append", default=[], help="Exact source_id; may be repeated")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--manifest-sha256", help="Expected SHA-256 of the manifest file, if independently recorded")
    parser.add_argument("--expected-samples", type=int)
    parser.add_argument("--expected-classes", type=int)
    parser.add_argument("--require-hashes", action="store_true", help="Fail if any selected manifest image_sha256 is absent")
    parser.add_argument("--no-check-extras", action="store_true")
    parser.add_argument("--max-errors", type=int, default=100)
    parser.add_argument("--report", type=Path, help="Optional JSON report; otherwise only stdout is used")
    args = parser.parse_args(argv)
    try:
        if args.manifest_only and args.output_root is not None:
            raise ReconstructionError("--manifest-only cannot be combined with --output-root")
        report = validate(args.manifest, args.output_root, sources=args.source, limit=args.limit,
                          manifest_sha256=args.manifest_sha256, expected_samples=args.expected_samples,
                          expected_classes=args.expected_classes, require_hashes=args.require_hashes,
                          check_extras=not args.no_check_extras, max_errors=args.max_errors,
                          classes_path=args.classes, summary_path=args.summary)
        if args.report:
            atomic_write(args.report, json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"), overwrite=True)
        summary = {key: value for key, value in report.items() if key != "by_class"}
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
