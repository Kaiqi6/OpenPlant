"""Frozen, annotation-grounded image recipes for the published OpenPlant release.

No legacy processing script is imported or executed. In particular, this module
never renames source files, randomly splits images, or deletes source data.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache
from pathlib import Path, PurePosixPath, PureWindowsPath

from PIL import Image

RECIPE_VERSION = "openplant-legacy-v1"
RECIPE_FIELDS = [
    "sample_id", "recipe_id", "operation", "annotation_path", "annotation_sha256",
    "annotation_id", "bbox_left", "bbox_top", "bbox_right", "bbox_bottom",
    "intermediate_format", "intermediate_mode", "recipe_version",
]
CROP_FAMILIES = {"cottonweeddet12", "weed25", "weednetr", "vcd", "imageweeds", "tobset"}
DIRECT_RECIPES = {"", "copy", "direct", "rgb_resize256_png_v1", "copy_resize256_png_v1"}


class ReconstructionError(ValueError):
    """A source or release record cannot be reproduced unambiguously."""


def normalized_id(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def crop_family(row):
    family = normalized_id(row.get("source_id", ""))
    if family in CROP_FAMILIES:
        return family
    # Stable source IDs may be prefixed with a release-specific numeric ID.
    for value in (row.get("source_name", ""), row.get("source_image_path", "").replace("\\", "/").split("/")[0]):
        key = normalized_id(value)
        if key in CROP_FAMILIES:
            return key
        if key == "dbmendeley":
            return "vcd"
    return None


def relative_path(value):
    """Validate a portable manifest path, including Windows drive/ADS hazards."""
    value = str(value).replace("\\", "/")
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or PureWindowsPath(value).drive
            or any(part in {"", ".", ".."} or ":" in part for part in value.split("/"))):
        raise ReconstructionError(f"Unsafe relative path: {value!r}")
    return path


def safe_join(root, value):
    root = Path(root).resolve()
    result = (root / Path(*relative_path(value).parts)).resolve()
    if not result.is_relative_to(root):
        raise ReconstructionError(f"Path escapes its root: {value!r}")
    return result


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path):
    opener = gzip.open if str(path).lower().endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def load_recipes(path):
    recipes = {}
    if path is None:
        return recipes
    if not Path(path).is_file():
        raise FileNotFoundError(f"Explicit recipe table does not exist: {path}")
    for row in csv_rows(path):
        sample_id = row.get("sample_id", "")
        if not sample_id or sample_id in recipes:
            raise ReconstructionError(f"Missing/duplicate recipe sample_id: {sample_id!r}")
        if row.get("operation") != "crop_jpeg":
            raise ReconstructionError(f"Unsupported recipe operation for {sample_id}")
        if row.get("recipe_version") != RECIPE_VERSION:
            raise ReconstructionError(f"Unsupported recipe version for {sample_id}")
        if row.get("intermediate_format") != "JPEG":
            raise ReconstructionError(f"Unsupported intermediate format for {sample_id}")
        if row.get("intermediate_mode") not in {"preserve", "rgb_if_rgba_or_p"}:
            raise ReconstructionError(f"Unsupported intermediate mode for {sample_id}")
        relative_path(row["annotation_path"])
        digest = row.get("annotation_sha256", "")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ReconstructionError(f"Missing/invalid annotation checksum for {sample_id}")
        try:
            box = tuple(int(row[f"bbox_{edge}"]) for edge in ("left", "top", "right", "bottom"))
        except (KeyError, ValueError) as exc:
            raise ReconstructionError(f"Invalid bounding box for {sample_id}") from exc
        if box[2] <= box[0] or box[3] <= box[1]:
            raise ReconstructionError(f"Empty bounding box for {sample_id}")
        recipes[sample_id] = row
    return recipes


def encoded_crop(source_image, recipe):
    """Reproduce the legacy JPEG intermediate, including its lossy round trip."""
    box = tuple(int(recipe[f"bbox_{edge}"]) for edge in ("left", "top", "right", "bottom"))
    crop = source_image.crop(box)
    if recipe["intermediate_mode"] == "rgb_if_rgba_or_p" and crop.mode in {"RGBA", "P"}:
        crop = crop.convert("RGB")
    buffer = io.BytesIO()
    # Legacy adapters called PIL.Image.save(path_with_jpg_suffix) without options.
    crop.save(buffer, format="JPEG")
    return buffer.getvalue()


class AnnotationReader:
    """Read source files or explicit ZIP members without extracting an archive.

    Aliases map expected path prefixes to actual path prefixes. They are explicit,
    not basename searches. ZIPs must be passed by the caller; nested ZIPs are not
    opened implicitly. Each archive is closed by close()/the context manager.
    """

    def __init__(self, root, archives=(), aliases=()):
        self.root = Path(root).resolve()
        self.archives = [zipfile.ZipFile(path) for path in archives]
        self.members = [set(archive.namelist()) for archive in self.archives]
        self.aliases = []
        for alias in aliases:
            expected, actual = alias.split("=", 1)
            expected = relative_path(expected.rstrip("/")).as_posix()
            actual = "" if not actual.strip("/") else relative_path(actual.strip("/")).as_posix()
            self.aliases.append((expected, actual))

    def close(self):
        for archive in self.archives:
            archive.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def candidate_paths(self, relative):
        value = relative_path(relative).as_posix()
        result = [value]
        for expected, actual in self.aliases:
            if value == expected or value.startswith(expected + "/"):
                tail = value[len(expected):].lstrip("/")
                result.append("/".join(part for part in (actual, tail) if part))
        return list(dict.fromkeys(result))

    @lru_cache(maxsize=128)
    def read(self, relative):
        candidates = self.candidate_paths(relative)
        for candidate in candidates:
            path = safe_join(self.root, candidate)
            if path.is_file():
                return path.read_bytes()
        matches = [(archive, candidate) for archive, names in zip(self.archives, self.members)
                   for candidate in candidates if candidate in names]
        if not matches:
            raise FileNotFoundError(f"Missing source/annotation: {relative}; checked extracted files and {len(self.archives)} explicit ZIPs")
        contents = [archive.read(member) for archive, member in matches]
        if len({hashlib.sha256(value).digest() for value in contents}) != 1:
            raise ReconstructionError(f"Ambiguous archive members for {relative}; use a narrower --archive/--alias selection")
        return contents[0]


WEED25_FOLDERS = {
    "bidens": "Budens pilosa", "billygoat weed": "billygoat_weed",
    "common dayflower": "Common_Datflower", "field thistle": "field_thistle",
    "green foxtail": "green_foxtail", "indian": "Indian_aster", "plantian": "plantain",
    "velvetleaf": "abutilon theophrasti", "white smart weed": "white_smart_weed",
}
IMAGEWEEDS_EXCLUDES = {
    "ImageWeeds_horseweed_5_01.jpg", "ImageWeeds_horseweed_8_02.jpg",
    "ImageWeeds_horseweed_20_02.jpg", "ImageWeeds_horseweed_5_02.jpg",
    "ImageWeeds_horseweed_8_03.jpg", "ImageWeeds_horseweed_15_01.jpg",
    "ImageWeeds_horseweed_20_01.jpg",
}


def accepted_box(box):
    width, height = box[2] - box[0], box[3] - box[1]
    return width >= 128 and height >= 128 and 0.5 <= width / height <= 2


class RecipeDeriver:
    """Enumerate original annotations and match their exact legacy output names.

    Output names identify enumerated annotations; they never supply coordinates.
    The coordinates always come from the source annotation and original image
    dimensions. Any absent or ambiguous correspondence fails explicitly.
    """

    def __init__(self, reader):
        self.reader = reader

    @lru_cache(maxsize=128)
    def candidates(self, family, source_path):
        source = relative_path(source_path)
        # The original adapters used the part before the FIRST dot, except TobSet.
        stem = source.name.split(".")[0] if family != "tobset" else source.stem
        if family == "cottonweeddet12":
            return self.coco_candidates(source_path)
        if family == "weed25":
            folder = WEED25_FOLDERS.get(source.parent.name, source.parent.name)
            annotation = f"Weed25/annatations/{folder}/{stem}.xml"
        elif family == "weednetr":
            annotation = f"WeedNet-R/dataset/Annotations/{stem}.xml"
        elif family == "vcd":
            # The historical VCD sheet stores img (a basename), not img_path.
            # This prefix is stated in VCD.py; it is not a fuzzy file search.
            if len(source.parts) == 1:
                source = PurePosixPath("DB_Mendeley/dataset") / source
            annotation = str(source.parent / (stem + ".xml"))
            try:
                self.reader.read(annotation)
            except FileNotFoundError:
                annotation = str(source.parent / (stem + ".json"))
        elif family == "tobset":
            match = re.fullmatch(r"tobacco_(\d{2})", source.parent.name)
            if not match:
                raise ReconstructionError(f"Unrecognized TobSet image folder: {source.parent}")
            annotation = str(source.parent.parent / ("labels_" + match[1]) / (stem + ".txt"))
        elif family == "imageweeds":
            annotation = str(source.parent.parent / "labels" / "TXT" / (stem + ".txt"))
        else:
            raise ReconstructionError(f"No annotation recipe for source {family}")
        payload = self.reader.read(annotation)
        records = []
        if annotation.endswith(".xml"):
            for index, obj in enumerate(ET.fromstring(payload).findall("object"), 1):
                label = obj.findtext("name")
                if family == "weednetr" and label != "crop":
                    continue
                if family == "vcd" and label not in {"maize", "bean", "leek"}:
                    continue
                bbox = obj.find("bndbox")
                cast = lambda value: int(float(value)) if family == "weednetr" else int(value)
                box = tuple(cast(bbox.findtext(key)) for key in ("xmin", "ymin", "xmax", "ymax"))
                if accepted_box(box):
                    records.append((f"object:{index}", box))
        elif annotation.endswith(".json"):
            for index, obj in enumerate(json.loads(payload)["objects"], 1):
                if obj["label"] not in {"maize", "bean", "leek"}:
                    continue
                box = obj["box"]
                box = (max(0, int(box["x_min"])), max(0, int(box["y_min"])), int(box["x_max"]), int(box["y_max"]))
                if accepted_box(box):
                    records.append((f"object:{index}", box))
        else:
            with Image.open(io.BytesIO(self.reader.read(source_path))) as image:
                image_width, image_height = image.size
            for index, line in enumerate(payload.decode("utf-8-sig").splitlines(), 1):
                label, x, y, width, height = map(float, line.split())
                if (family == "tobset" and label != 0) or (family == "imageweeds" and int(label) not in range(4)):
                    continue
                width, height, x, y = width * image_width, height * image_height, x * image_width, y * image_height
                box = (int(x - width / 2), int(y - height / 2), int(x + width / 2), int(y + height / 2))
                if accepted_box(box):
                    records.append((f"line:{index}", box))
        prefix = {"weed25": "Weed25", "weednetr": "WeedNet-R", "vcd": "VCD", "imageweeds": "ImageWeeds", "tobset": "TobSet"}[family]
        name_stem = f"{source.parent.name}_{stem}" if family == "tobset" else stem
        results = {}
        for counter, (annotation_id, box) in enumerate(records, 1):
            name = f"{prefix}_{name_stem}_{counter:02d}.jpg"
            if family == "imageweeds" and name in IMAGEWEEDS_EXCLUDES:
                continue
            results[name] = (annotation, hashlib.sha256(payload).hexdigest(), annotation_id, box)
        return results

    @lru_cache(maxsize=1)
    def coco_index(self):
        annotation = "CottonWeedDet12/weedcoco.json"
        payload = self.reader.read(annotation)
        data = json.loads(payload)
        images = {image["id"]: image["file_name"].replace("\\", "/") for image in data["images"]}
        checksum = hashlib.sha256(payload).hexdigest()
        indexed = {}
        for obj in data["annotations"]:
            if obj["category_id"] in {1, 7}:
                continue
            x, y, width, height = map(int, obj["bbox"])
            key = f"CottonWeedDet12/images/{images[obj['image_id']]}"
            indexed.setdefault(key, {})[f"CWD12_{obj['id']}.jpg"] = (
                annotation, checksum, str(obj["id"]), (x, y, x + width, y + height))
        return indexed

    def coco_candidates(self, source_path):
        return self.coco_index().get(source_path.replace("\\", "/"), {})

    def derive(self, row):
        family = crop_family(row)
        if not family:
            return None
        name = relative_path(row["curated_path"]).name
        candidates = self.candidates(family, row["source_image_path"])
        if name not in candidates:
            raise ReconstructionError(f"{row['sample_id']}: {name} does not correspond to an accepted annotation in {row['source_image_path']}; cannot infer a crop")
        annotation, checksum, annotation_id, box = candidates[name]
        return dict(zip(RECIPE_FIELDS, [
            row["sample_id"], row.get("recipe_id") or row["sample_id"], "crop_jpeg",
            annotation, checksum, annotation_id, *map(str, box), "JPEG",
            "rgb_if_rgba_or_p" if family == "imageweeds" else "preserve", RECIPE_VERSION,
        ]))
