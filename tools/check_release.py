"""Check published metadata joins, configuration/asset integrity, and local links.

Uses only release files. It does not download images or inspect a local dataset.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


def check(root):
    errors = []
    summary = json.loads((root / "metadata/summary.json").read_text(encoding="utf-8"))
    sources = json.loads((root / "metadata/sources.json").read_text(encoding="utf-8"))["sources"]
    if len(sources) != 41 or len({s["source_id"] for s in sources}) != 41:
        errors.append("Expected 41 unique source catalogue entries")
    contributed = {s["source_id"]: s["mapped_samples"] for s in sources if s["mapped_samples"] is not None}
    if contributed != summary["sources"]:
        errors.append("Source catalogue contributions differ from manifest summary")
    with (root / "metadata/classes.csv").open(encoding="utf-8", newline="") as stream:
        classes = list(csv.DictReader(stream))
    if len(classes) != summary["classes"] or sum(int(r["total_count"]) for r in classes) != summary["samples"]:
        errors.append("Class totals differ from summary")
    configs = list((root / "configs").glob("*.json"))
    if len(configs) != 16:
        errors.append("Expected 16 CNN/ViT configs")
    for path in configs:
        config = json.loads(path.read_text(encoding="utf-8"))
        if config["num_classes"] != len(classes):
            errors.append(f"Wrong class count in {path.name}")
        weight = root / config["provenance"]["legacy_weight"]
        if not weight.is_file():
            errors.append(f"Missing checkpoint path: {weight.relative_to(root)}")
    provenance = json.loads((root / "assets/figures/provenance.json").read_text(encoding="utf-8"))
    for record in provenance["files"]:
        path = root / "assets/figures" / record["file"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"Missing/changed figure: {record['file']}")
    for document in [root / "README.md", root / "DATA_LICENSE.md", *(root / "docs").glob("*.md")]:
        content = document.read_text(encoding="utf-8")
        # Explicit markdown destinations and HTML image sources, excluding fragments/URLs.
        links = re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", content)
        links.extend(re.findall(r'src="([^"]+)"', content))
        for link in links:
            parts = urlsplit(link)
            if parts.scheme or not parts.path:
                continue
            target = (document.parent / unquote(parts.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"Broken local link in {document.relative_to(root)}: {link}")
    if errors:
        for error in errors:
            print("ERROR: " + error, file=sys.stderr)
        return 1
    print(json.dumps({"sources": len(sources), "mapped_sources": len(contributed),
                      "samples": summary["samples"], "classes": len(classes),
                      "model_configs": len(configs), "paper_assets": len(provenance["files"]),
                      "local_links": "passed"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(check(Path(__file__).resolve().parents[1]))
