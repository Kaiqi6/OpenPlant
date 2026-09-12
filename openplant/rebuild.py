"""Reconstruct exactly the samples and splits in a frozen OpenPlant manifest."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION

from .recipes import (DIRECT_RECIPES, AnnotationReader, RecipeDeriver, ReconstructionError,
                      crop_family, csv_rows, encoded_crop, load_recipes, relative_path,
                      safe_join, sha256_file)

REQUIRED_FIELDS = {
    "sample_id", "source_id", "source_image_path", "class_id", "class_name", "split",
    "curated_path", "image_path", "source_sha256", "image_sha256", "recipe_id",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".jfif", ".bmp", ".tif", ".tiff", ".webp"}


def iter_manifest(path):
    seen_ids, seen_paths = set(), set()
    id_to_name, name_to_id = {}, {}
    found = False
    for number, row in enumerate(csv_rows(path), 2):
        found = True
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            raise ReconstructionError(f"Manifest missing columns: {', '.join(sorted(missing))}")
        if None in row or any(value is None for value in row.values()):
            raise ReconstructionError(f"Malformed CSV record at line {number}")
        sample_id = row["sample_id"]
        if not sample_id or sample_id in seen_ids:
            raise ReconstructionError(f"Missing/duplicate sample_id at line {number}: {sample_id!r}")
        seen_ids.add(sample_id)
        for field in ("source_image_path", "curated_path", "image_path"):
            row[field] = relative_path(row[field]).as_posix()
        output = relative_path(row["image_path"])
        if len(output.parts) != 3 or output.parts[:2] != (row["split"], row["class_name"]) or output.suffix != ".png":
            raise ReconstructionError(f"{sample_id}: image_path must be split/class_name/filename.png")
        if row["split"] not in {"train", "val", "test"}:
            raise ReconstructionError(f"{sample_id}: invalid split {row['split']!r}")
        # Windows is case-insensitive. A release must also be safe on that platform.
        key = row["image_path"].casefold()
        if key in seen_paths:
            raise ReconstructionError(f"Duplicate output path: {row['image_path']}")
        seen_paths.add(key)
        class_id, class_name = row["class_id"], row["class_name"]
        if not class_id or not class_name or not row["source_id"]:
            raise ReconstructionError(f"{sample_id}: missing source/class identifier")
        if id_to_name.setdefault(class_id, class_name) != class_name or name_to_id.setdefault(class_name, class_id) != class_id:
            raise ReconstructionError(f"{sample_id}: inconsistent class_id/class_name mapping")
        for field in ("source_sha256", "curated_sha256", "image_sha256"):
            digest = row.get(field, "")
            if digest and not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                raise ReconstructionError(f"{sample_id}: invalid {field}")
            if digest:
                row[field] = digest.lower()
        if row.get("image_bytes") and (not row["image_bytes"].isdigit() or int(row["image_bytes"]) <= 0):
            raise ReconstructionError(f"{sample_id}: invalid image_bytes")
        yield row
    if not found:
        raise ReconstructionError("Manifest contains no samples")


def selection(rows, sources=(), limit=None):
    selected = []
    available = set()
    for row in rows:
        available.add(row["source_id"])
        if sources and row["source_id"] not in sources:
            continue
        if limit is None or len(selected) < limit:
            selected.append(row)
    unknown = set(sources) - available
    if unknown:
        raise ReconstructionError(f"Unknown --source IDs: {', '.join(sorted(unknown))}; use source_id values from metadata/sources.csv")
    if not selected:
        raise ReconstructionError("No samples selected")
    return selected


def selected_rows(manifest, sources=(), limit=None):
    """Second-pass iterator after manifest_statistics has checked the whole file."""
    count = 0
    for row in csv_rows(manifest):
        if sources and row["source_id"] not in sources:
            continue
        if limit is not None and count >= limit:
            break
        for field in ("source_image_path", "curated_path", "image_path"):
            row[field] = relative_path(row[field]).as_posix()
        for field in ("source_sha256", "curated_sha256", "image_sha256"):
            if row.get(field):
                row[field] = row[field].lower()
        count += 1
        yield row


def manifest_statistics(manifest, sources=(), limit=None, collect_paths=False):
    stats = {"samples": 0, "classes": {}, "splits": Counter(), "sources": Counter(),
             "class_splits": Counter(), "selected": 0, "selected_splits": Counter(),
             "selected_sources": Counter(), "selected_classes": Counter()}
    if collect_paths:
        stats["paths"] = set()
    for row in iter_manifest(manifest):
        stats["samples"] += 1
        stats["classes"][row["class_id"]] = row["class_name"]
        stats["splits"][row["split"]] += 1
        stats["sources"][row["source_id"]] += 1
        stats["class_splits"][(row["class_id"], row["split"])] += 1
        if collect_paths:
            stats["paths"].add(row["image_path"])
        if (not sources or row["source_id"] in sources) and (limit is None or stats["selected"] < limit):
            stats["selected"] += 1
            stats["selected_splits"][row["split"]] += 1
            stats["selected_sources"][row["source_id"]] += 1
            stats["selected_classes"][row["class_id"]] += 1
    unknown = set(sources) - stats["sources"].keys()
    if unknown:
        raise ReconstructionError(f"Unknown --source IDs: {', '.join(sorted(unknown))}; use source_id values from metadata/sources.csv")
    if not stats["selected"]:
        raise ReconstructionError("No samples selected")
    return stats


def load_path_map(path):
    result = {}
    if path is None:
        return result
    for row in csv_rows(path):
        if not {"source_id", "source_image_path", "downloaded_path"}.issubset(row):
            raise ReconstructionError("--path-map requires source_id,source_image_path,downloaded_path columns")
        if not row["source_id"]:
            raise ReconstructionError("Empty source_id in path map")
        key = (row["source_id"], relative_path(row["source_image_path"]).as_posix())
        if key in result:
            raise ReconstructionError(f"Duplicate path-map entry: {key}")
        result[key] = relative_path(row["downloaded_path"]).as_posix()
    return result


def resize_rgb_png(image):
    """Legacy torchvision Resize(256): RGB, short edge 256, PIL bilinear."""
    image = image.convert("RGB")
    width, height = image.size
    if width <= height:
        size = (256, int(256 * height / width))
    else:
        size = (int(256 * width / height), 256)
    if image.size != size:
        image = image.resize(size, resample=Image.Resampling.BILINEAR)
    result = io.BytesIO()
    image.save(result, format="PNG")
    return result.getvalue()


def verify_digest(actual, expected, label):
    if expected and actual != expected.lower():
        raise ReconstructionError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")


class SourceResolver:
    def __init__(self, root, allow_index=False, aliases=(), path_map=None):
        self.root = Path(root).resolve()
        self.allow_index = allow_index
        self.index = None
        self.hash_cache = {}
        self.paths = AnnotationReader(root, aliases=aliases)
        self.path_map = path_map or {}

    def digest(self, path):
        if path not in self.hash_cache:
            self.hash_cache[path] = sha256_file(path)
        return self.hash_cache[path]

    def build_index(self):
        self.index = {}
        print("Indexing source image content for renamed files (read only)...", file=sys.stderr)
        count = 0
        for directory, dirs, files in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(name for name in dirs if not Path(directory, name).is_symlink())
            for name in sorted(files):
                path = Path(directory, name)
                if path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                resolved = path.resolve()
                if not resolved.is_relative_to(self.root):
                    continue
                digest = self.digest(resolved)
                self.index.setdefault(digest, resolved)
                count += 1
                if count % 10000 == 0:
                    print(f"Indexed {count:,} source images", file=sys.stderr)

    def resolve(self, row):
        expected = row.get("source_sha256", "")
        key = (row["source_id"], row["source_image_path"])
        if key in self.path_map:
            path = safe_join(self.root, self.path_map[key])
            if not path.is_file():
                raise ReconstructionError(f"Explicit path-map target is missing: {self.path_map[key]}")
            if expected:
                verify_digest(self.digest(path), expected, "Explicit path-map source")
            return path
        mismatch = None
        candidates = self.paths.candidate_paths(row["source_image_path"])
        if crop_family(row) == "vcd" and len(relative_path(row["source_image_path"]).parts) == 1:
            candidates.extend(self.paths.candidate_paths("DB_Mendeley/dataset/" + row["source_image_path"]))
        for relative in candidates:
            path = safe_join(self.root, relative)
            if path.is_file():
                if not expected or self.digest(path) == expected:
                    return path
                mismatch = path
        if mismatch is not None and not self.allow_index:
            verify_digest(self.digest(mismatch), expected, f"{row['sample_id']} source")
        if self.allow_index and expected:
            if self.index is None:
                self.build_index()
            if expected in self.index:
                return self.index[expected]
        reason = " (content matching needs source_sha256)" if self.allow_index and not expected else ""
        raise ReconstructionError(f"{row['sample_id']}: missing or changed source {row['source_image_path']}{reason}; unpack the documented source version or provide an explicit --path-map for renamed files; --index-source additionally requires a verified source_sha256")


def ensure_disjoint(source_root, output_root):
    source, output = Path(source_root).resolve(), Path(output_root).resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ReconstructionError("--source-root and --output-root must be separate, non-overlapping directories")
    if not source.is_dir():
        raise ReconstructionError(f"Source root is not a directory: {source}")
    return source, output


def atomic_write(path, payload, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise ReconstructionError(f"Refusing to overwrite existing file: {path}; use --resume to verify it")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".openplant-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        if not overwrite and path.exists():
            raise ReconstructionError(f"Output appeared during reconstruction: {path}")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def render_sample(row, source_path, recipe=None):
    if recipe is None and crop_family(row):
        raise ReconstructionError(f"{row['sample_id']}: missing annotation-grounded crop recipe; run tools/enrich_recipes.py with the original annotations")
    if recipe is not None:
        expected_id = row.get("recipe_id", "")
        if expected_id and expected_id != recipe["recipe_id"]:
            raise ReconstructionError(f"{row['sample_id']}: recipe_id mismatch")
    elif row.get("recipe_id", "") not in DIRECT_RECIPES:
        raise ReconstructionError(f"{row['sample_id']}: unsupported recipe_id {row['recipe_id']!r}")
    with Image.open(source_path) as original:
        if recipe is None:
            if row.get("curated_sha256"):
                verify_digest(sha256_file(source_path), row["curated_sha256"], "Curated copy")
            payload = resize_rgb_png(original)
        else:
            intermediate = encoded_crop(original, recipe)
            verify_digest(hashlib.sha256(intermediate).hexdigest(), row.get("curated_sha256", ""), "Curated JPEG (check Pillow/libjpeg versions)")
            with Image.open(io.BytesIO(intermediate)) as decoded:
                payload = resize_rgb_png(decoded)
    verify_digest(hashlib.sha256(payload).hexdigest(), row.get("image_sha256", ""), "Output PNG (check Pillow/zlib versions)")
    if row.get("image_bytes") and len(payload) != int(row["image_bytes"]):
        raise ReconstructionError(f"{row['sample_id']}: output byte length does not match manifest")
    return payload


def rebuild(manifest, source_root, output_root, *, recipes_path=None, sources=(), limit=None,
            resume=False, index_source=False, max_errors=20, aliases=(), path_map=None):
    source_root, output_root = ensure_disjoint(source_root, output_root)
    if limit is not None and limit <= 0:
        raise ReconstructionError("--limit must be positive")
    if max_errors <= 0:
        raise ReconstructionError("--max-errors must be positive")
    stats = manifest_statistics(manifest, sources, limit)
    recipes = load_recipes(recipes_path)
    resolver = SourceResolver(source_root, index_source, aliases, load_path_map(path_map))
    annotations = AnnotationReader(source_root, aliases=aliases)
    deriver = RecipeDeriver(annotations)
    report = {"manifest_sha256": sha256_file(manifest), "pillow_version": PILLOW_VERSION,
              "selected": stats["selected"], "partial": bool(sources or limit), "written": 0,
              "resumed": 0, "unverified_source_hashes": 0, "unverified_image_hashes": 0,
              "errors": [], "by_split": dict(stats["selected_splits"]),
              "by_source": dict(stats["selected_sources"])}
    checked_annotations = set()
    for position, row in enumerate(selected_rows(manifest, sources, limit), 1):
        try:
            destination = safe_join(output_root, row["image_path"])
            if destination.exists():
                if not resume:
                    raise ReconstructionError(f"Existing output {row['image_path']}; use --resume to verify it")
                if row.get("image_sha256"):
                    verify_digest(sha256_file(destination), row["image_sha256"], "Existing output")
                    if row.get("image_bytes") and destination.stat().st_size != int(row["image_bytes"]):
                        raise ReconstructionError("Existing output byte length does not match manifest")
                    report["resumed"] += 1
                    continue
            source = resolver.resolve(row)
            recipe = recipes.get(row["sample_id"])
            if recipe is None and crop_family(row):
                recipe = deriver.derive(row)
            if recipe is not None:
                annotation_key = (recipe["annotation_path"], recipe["annotation_sha256"])
                if annotation_key not in checked_annotations:
                    payload = annotations.read(recipe["annotation_path"])
                    verify_digest(hashlib.sha256(payload).hexdigest(), recipe["annotation_sha256"], "Annotation")
                    checked_annotations.add(annotation_key)
            payload = render_sample(row, source, recipe)
            if destination.exists():
                verify_digest(sha256_file(destination), hashlib.sha256(payload).hexdigest(), "Existing output versus reconstructed bytes")
                report["resumed"] += 1
            else:
                atomic_write(destination, payload)
                report["written"] += 1
            report["unverified_source_hashes"] += not bool(row.get("source_sha256"))
            report["unverified_image_hashes"] += not bool(row.get("image_sha256"))
        except (OSError, ValueError, KeyError, SyntaxError, Image.DecompressionBombError) as exc:
            report["errors"].append({"sample_id": row["sample_id"], "source_id": row["source_id"], "message": str(exc)})
            print(f"ERROR {row['sample_id']}: {exc}", file=sys.stderr)
            if len(report["errors"]) >= max_errors:
                report["stopped_early"] = position < stats["selected"]
                break
        if position % 1000 == 0:
            print(f"Processed {position:,}/{stats['selected']:,} selected samples", file=sys.stderr)
    report["ok"] = not report["errors"] and report["written"] + report["resumed"] == stats["selected"]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "metadata/manifest.csv.gz")
    parser.add_argument("--recipes", type=Path, help="Optional annotation-grounded recipe table; omitted: derive from source annotations at runtime")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source", action="append", default=[], help="Exact source_id; repeat for multiple sources")
    parser.add_argument("--limit", type=int, help="Smoke check only: first N selected manifest rows")
    parser.add_argument("--resume", action="store_true", help="Verify existing output; never overwrite mismatches")
    parser.add_argument("--index-source", action="store_true", help="Read-only SHA-256 search for renamed byte-identical source images")
    parser.add_argument("--alias", action="append", default=[], metavar="EXPECTED=ACTUAL", help="Explicit source/annotation directory prefix mapping inside source-root")
    parser.add_argument("--path-map", type=Path, help="CSV with source_id,source_image_path,downloaded_path; explicit per-file overrides")
    parser.add_argument("--max-errors", type=int, default=20)
    parser.add_argument("--report", type=Path, help="Default: OUTPUT_ROOT/build_report.json")
    args = parser.parse_args(argv)
    try:
        source, output = ensure_disjoint(args.source_root, args.output_root)
        report_path = (args.report or output / "build_report.json").resolve()
        if report_path.is_relative_to(source):
            raise ReconstructionError("Report must not be written inside the source root")
        report = rebuild(args.manifest, source, output, recipes_path=args.recipes, sources=args.source,
                         limit=args.limit, resume=args.resume, index_source=args.index_source,
                         max_errors=args.max_errors, aliases=args.alias, path_map=args.path_map)
        atomic_write(report_path, json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"), overwrite=True)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
