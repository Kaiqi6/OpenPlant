"""Export annotation-grounded crop recipes after users obtain source datasets.

This tool does not download, rename, crop, or alter source images. It reads source
annotations (and image dimensions for YOLO records) and writes a separate table.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openplant.rebuild import atomic_write, manifest_statistics, selected_rows
from openplant.recipes import AnnotationReader, RECIPE_FIELDS, RecipeDeriver, ReconstructionError, crop_family


def export_recipes(manifest, source_root, output, *, archives=(), aliases=(), sources=(), limit=None):
    root, output = Path(source_root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ReconstructionError("Recipe output must be outside the source root")
    if output.exists():
        raise ReconstructionError(f"Output already exists: {output}; choose a new versioned filename")
    stats = manifest_statistics(manifest, sources, limit)
    records, errors = [], []
    with AnnotationReader(root, archives=archives, aliases=aliases) as reader:
        deriver = RecipeDeriver(reader)
        for row in selected_rows(manifest, sources, limit):
            if not crop_family(row):
                continue
            try:
                records.append(deriver.derive(row))
            except (OSError, ValueError, KeyError, SyntaxError, Image.DecompressionBombError) as exc:
                errors.append({"sample_id": row["sample_id"], "source_id": row["source_id"], "message": str(exc)})
                if len(errors) >= 20:
                    break
    if errors:
        # Never publish an incomplete recipe table as a successful release.
        print(json.dumps({"ok": False, "errors": errors, "output_written": False}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=RECIPE_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    payload = text.getvalue().encode("utf-8")
    if str(output).lower().endswith(".gz"):
        payload = gzip.compress(payload, mtime=0)
    atomic_write(output, payload)
    print(json.dumps({"ok": True, "selected_manifest_rows": stats["selected"], "crop_recipes": len(records),
                      "partial": bool(sources or limit), "output": str(output),
                      "annotation_files": len({row["annotation_path"] for row in records})}, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "metadata/manifest.csv.gz")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--archive", type=Path, action="append", default=[], help="Explicit ZIP containing source annotations/images; no extraction")
    parser.add_argument("--alias", action="append", default=[], metavar="EXPECTED=ACTUAL", help="Explicit directory prefix mapping, including archive member prefixes")
    args = parser.parse_args(argv)
    try:
        if args.limit is not None and args.limit <= 0:
            raise ReconstructionError("--limit must be positive")
        return export_recipes(args.manifest, args.source_root, args.output, archives=args.archive,
                              aliases=args.alias, sources=args.source, limit=args.limit)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
