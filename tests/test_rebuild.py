"""Synthetic-data regression tests: never inspect the author's image collection."""
import csv
import gzip
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from openplant.rebuild import (REQUIRED_FIELDS, ensure_disjoint, iter_manifest,
                               rebuild, render_sample, resize_rgb_png)
from openplant.recipes import (AnnotationReader, RecipeDeriver, ReconstructionError,
                               encoded_crop, safe_join, sha256_file)
from openplant.validate import validate


class RebuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "sources"
        self.output = self.root / "rebuilt"
        self.source.mkdir()

    def make_image(self, relative, size=(320, 481), mode="RGB"):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new(mode, size, "green")
        image.save(path)
        return path

    def row(self, source_path="Example/raw.png", source_id="example", curated="train/Plant/raw.png", **changes):
        row = {key: "" for key in REQUIRED_FIELDS}
        row.update(sample_id="s1", source_id=source_id, source_image_path=source_path,
                   class_id="0", class_name="Plant", split="train", curated_path=curated,
                   image_path=f"train/Plant/{Path(curated).stem}.png")
        row.update(changes)
        return row

    def manifest(self, *rows):
        path = self.root / "manifest.csv.gz"
        fields = sorted(set().union(*(row.keys() for row in rows)))
        with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def write(self, relative, content):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    @staticmethod
    def xml(*objects):
        return "<annotation>" + "".join(
            f"<object><name>{label}</name><bndbox><xmin>{box[0]}</xmin><ymin>{box[1]}</ymin>"
            f"<xmax>{box[2]}</xmax><ymax>{box[3]}</ymax></bndbox></object>" for label, box in objects
        ) + "</annotation>"

    def test_direct_build_exact_hash_and_frozen_split(self):
        source = self.make_image("Example/raw.png")
        before = source.read_bytes()
        with Image.open(source) as image:
            expected = resize_rgb_png(image)
        row = self.row(source_sha256=sha256_file(source), curated_sha256=sha256_file(source),
                       image_sha256=hashlib.sha256(expected).hexdigest(), image_bytes=str(len(expected)))
        manifest = self.manifest(row)
        report = rebuild(manifest, self.source, self.output)
        self.assertTrue(report["ok"])
        self.assertEqual((self.output / row["image_path"]).read_bytes(), expected)
        self.assertEqual(source.read_bytes(), before)
        with Image.open(self.output / row["image_path"]) as image:
            self.assertEqual(image.size, (256, 384))
        audit = validate(manifest, self.output, expected_samples=1, expected_classes=1, require_hashes=True)
        self.assertTrue(audit["byte_identity_verified"])

    def test_resume_checks_existing_bytes_without_overwrite(self):
        self.make_image("Example/raw.png")
        manifest = self.manifest(self.row())
        self.assertTrue(rebuild(manifest, self.source, self.output)["ok"])
        self.assertEqual(rebuild(manifest, self.source, self.output, resume=True)["resumed"], 1)
        path = self.output / "train/Plant/raw.png"
        path.write_bytes(b"damaged")
        self.assertFalse(rebuild(manifest, self.source, self.output, resume=True)["ok"])
        self.assertEqual(path.read_bytes(), b"damaged")

    def test_existing_output_requires_resume(self):
        self.make_image("Example/raw.png")
        manifest = self.manifest(self.row())
        rebuild(manifest, self.source, self.output)
        self.assertFalse(rebuild(manifest, self.source, self.output)["ok"])

    def test_source_hash_failure_is_reported(self):
        self.make_image("Example/raw.png")
        report = rebuild(self.manifest(self.row(source_sha256="0" * 64)), self.source, self.output)
        self.assertFalse(report["ok"])
        self.assertIn("SHA-256 mismatch", report["errors"][0]["message"])

    def test_renamed_source_can_be_resolved_by_content(self):
        renamed = self.make_image("original_download/original-name.png")
        row = self.row(source_sha256=sha256_file(renamed))
        report = rebuild(self.manifest(row), self.source, self.output, index_source=True)
        self.assertTrue(report["ok"])
        self.assertTrue(renamed.exists())

    def test_explicit_alias_changes_layout_without_renaming_source(self):
        image = self.make_image("actual_archive_root/raw.png")
        report = rebuild(self.manifest(self.row()), self.source, self.output,
                         aliases=["Example=actual_archive_root"])
        self.assertTrue(report["ok"])
        self.assertTrue(image.exists())

    def test_missing_source_has_non_success_report(self):
        report = rebuild(self.manifest(self.row()), self.source, self.output)
        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["sample_id"], "s1")

    def test_explicit_path_map_resolves_old_name_without_guessing(self):
        original = self.make_image("original_download/author-photo.png")
        mapping = self.root / "path_map.csv"
        mapping.write_text("source_id,source_image_path,downloaded_path\nexample,Example/raw.png,original_download/author-photo.png\n", encoding="utf-8")
        report = rebuild(self.manifest(self.row()), self.source, self.output, path_map=mapping)
        self.assertTrue(report["ok"])
        self.assertTrue(original.exists())
        mapping.write_text("source_id,source_image_path,downloaded_path\nexample,Example/raw.png,../outside.png\n", encoding="utf-8")
        with self.assertRaises(ReconstructionError):
            rebuild(self.manifest(self.row()), self.source, self.output, path_map=mapping)

    def test_classes_and_summary_cross_checks(self):
        manifest = self.manifest(self.row())
        classes = self.root / "classes.csv"
        classes.write_text("class_id,class_name,train_count,val_count,test_count,total_count\n0,Plant,1,0,0,1\n", encoding="utf-8")
        summary = self.root / "summary.json"
        summary.write_text(json.dumps({"samples": 1, "classes": 1, "source_groups": 1,
            "splits": {"train": 1}, "sources": {"example": 1}, "manifest_sha256": sha256_file(manifest)}), encoding="utf-8")
        self.assertTrue(validate(manifest, classes_path=classes, summary_path=summary)["ok"])
        classes.write_text("class_id,class_name,train_count,val_count,test_count,total_count\n0,Plant,0,1,0,1\n", encoding="utf-8")
        with self.assertRaises(ReconstructionError):
            validate(manifest, classes_path=classes)
        summary.write_text("{}", encoding="utf-8")
        with self.assertRaises(ReconstructionError):
            validate(manifest, summary_path=summary)

    def test_no_path_traversal_or_overlapping_roots(self):
        for path in ("../out.png", "C:/out.png", "/out.png", "a/../../out.png", "a/file:stream", "a//b"):
            with self.subTest(path=path), self.assertRaises(ReconstructionError):
                safe_join(self.source, path)
        with self.assertRaises(ReconstructionError):
            ensure_disjoint(self.source, self.source / "output")
        with self.assertRaises(ReconstructionError):
            ensure_disjoint(self.source, self.root)

    def test_duplicate_manifest_paths_and_class_mismatch_rejected(self):
        with self.assertRaises(ReconstructionError):
            list(iter_manifest(self.manifest(self.row(), self.row(sample_id="s2"))))
        with self.assertRaises(ReconstructionError):
            list(iter_manifest(self.manifest(self.row(), self.row(sample_id="s2", class_name="Other",
                                                                 image_path="test/Other/b.png", split="test"))))

    def test_filter_limit_and_unknown_source(self):
        self.make_image("Example/raw.png")
        rows = [self.row(), self.row(sample_id="s2", source_id="missing", curated_path="test/Plant/missing.jpg",
                                    image_path="test/Plant/missing.png", split="test", source_image_path="missing/a.jpg")]
        manifest = self.manifest(*rows)
        report = rebuild(manifest, self.source, self.output, sources=["example"], limit=1)
        self.assertTrue(report["ok"])
        self.assertTrue(report["partial"])
        with self.assertRaises(ReconstructionError):
            rebuild(manifest, self.source, self.output, sources=["typo"])

    def test_validator_metadata_only_and_empty_hash_semantics(self):
        manifest = self.manifest(self.row())
        report = validate(manifest)
        self.assertTrue(report["ok"])
        self.assertFalse(report["byte_identity_verified"])
        self.assertEqual(report["missing_image_hashes"], 1)
        self.assertFalse(validate(manifest, require_hashes=True)["ok"])
        with self.assertRaises(ReconstructionError):
            validate(manifest, manifest_sha256="0" * 64)

    def test_validator_detects_unexpected_images(self):
        self.make_image("Example/raw.png")
        manifest = self.manifest(self.row())
        rebuild(manifest, self.source, self.output)
        extra = self.output / "train/Plant/extra.png"
        Image.new("RGB", (256, 256)).save(extra)
        report = validate(manifest, self.output)
        self.assertFalse(report["ok"])
        self.assertEqual(report["unexpected_image_count"], 1)

    def test_weed25_filter_counter_comes_from_annotations(self):
        source = self.make_image("Weed25/bidens/plant.jpg", (512, 512))
        annotation = self.write("Weed25/annatations/Budens pilosa/plant.xml", self.xml(
            ("weed", (0, 0, 20, 20)), ("weed", (20, 30, 240, 250)), ("weed", (100, 100, 300, 300))))
        row = self.row("Weed25/bidens/plant.jpg", "weed25", "train/Plant/Weed25_plant_01.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "object:2")
        self.assertEqual(recipe["bbox_left"], "20")
        self.assertEqual(recipe["annotation_sha256"], sha256_file(annotation))
        # Dynamic recipes work without a pre-exported recipes table.
        report = rebuild(self.manifest(row), self.source, self.output)
        self.assertTrue(report["ok"])
        self.assertTrue(source.exists())

    def test_crop_name_without_corresponding_annotation_fails(self):
        self.make_image("Weed25/bidens/plant.jpg", (512, 512))
        self.write("Weed25/annatations/Budens pilosa/plant.xml", self.xml(("weed", (0, 0, 200, 200))))
        row = self.row("Weed25/bidens/plant.jpg", "weed25", "train/Plant/Weed25_plant_99.jpg")
        self.assertFalse(rebuild(self.manifest(row), self.source, self.output)["ok"])

    def test_weednet_crop_label_and_float_coordinates(self):
        self.make_image("WeedNet-R/dataset/JPEGImages/1.jpg", (512, 512))
        self.write("WeedNet-R/dataset/Annotations/1.xml", self.xml(
            ("weed", (0, 0, 200, 200)), ("crop", (10.9, 20.1, 220.8, 230.7))))
        row = self.row("WeedNet-R/dataset/JPEGImages/1.jpg", "weednetr", "train/Plant/WeedNet-R_1_01.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "object:2")
        self.assertEqual(recipe["bbox_left"], "10")

    def test_vcd_json_clamping_and_filter(self):
        self.make_image("DB_Mendeley/dataset/plant.jpg", (512, 512))
        self.write("DB_Mendeley/dataset/plant.json", json.dumps({"objects": [
            {"label": "weed", "box": {"x_min": 0, "y_min": 0, "x_max": 250, "y_max": 250}},
            {"label": "maize", "box": {"x_min": -10, "y_min": -20, "x_max": 200, "y_max": 220}},
        ]}))
        row = self.row("DB_Mendeley/dataset/plant.jpg", "vcd", "train/Plant/VCD_plant_01.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "object:2")
        self.assertEqual(recipe["bbox_top"], "0")

    def test_vcd_historical_basename_resolves_documented_source_directory(self):
        self.make_image("DB_Mendeley/dataset/plant.jpg", (512, 512))
        self.write("DB_Mendeley/dataset/plant.xml", self.xml(("maize", (0, 0, 200, 200))))
        row = self.row("plant.jpg", "VCD", "train/Plant/VCD_plant_01.jpg")
        self.assertTrue(rebuild(self.manifest(row), self.source, self.output)["ok"])

    def test_coco_uses_annotation_id_and_integer_xywh(self):
        self.make_image("CottonWeedDet12/images/a.jpg", (512, 512))
        self.write("CottonWeedDet12/weedcoco.json", json.dumps({
            "images": [{"id": 4, "file_name": "a.jpg"}],
            "annotations": [{"id": 27, "image_id": 4, "category_id": 0, "bbox": [1.9, 2.8, 150.9, 180.1]}]}))
        row = self.row("CottonWeedDet12/images/a.jpg", "cottonweeddet12", "train/Plant/CWD12_27.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "27")
        self.assertEqual(recipe["bbox_right"], "151")

    def test_tobset_yolo_dimensions_and_class_filter(self):
        self.make_image("TobSet/tobacco_01/a.jpg", (400, 600))
        self.write("TobSet/labels_01/a.txt", "1 0.5 0.5 0.8 0.8\n0 0.5 0.5 0.5 0.5\n")
        row = self.row("TobSet/tobacco_01/a.jpg", "tobset", "train/Plant/TobSet_tobacco_01_a_01.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "line:2")
        self.assertEqual(recipe["bbox_right"], "300")
        self.assertEqual(recipe["bbox_bottom"], "450")

    def test_imageweeds_exclusions_preserve_original_counter(self):
        self.make_image("ImageWeeds/Individual_Weed/horseweed/images/horseweed_5.jpg", (512, 512))
        self.write("ImageWeeds/Individual_Weed/horseweed/labels/TXT/horseweed_5.txt",
                   "1 0.5 0.5 0.5 0.5\n1 0.5 0.5 0.5 0.5\n1 0.5 0.5 0.5 0.5\n")
        row = self.row("ImageWeeds/Individual_Weed/horseweed/images/horseweed_5.jpg", "imageweeds",
                       "train/Plant/ImageWeeds_horseweed_5_03.jpg")
        with AnnotationReader(self.source) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["annotation_id"], "line:3")
        self.assertEqual(recipe["intermediate_mode"], "rgb_if_rgba_or_p")

    def test_zip_annotations_require_explicit_alias(self):
        archive = self.root / "annotations.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("archive-root/1.xml", self.xml(("crop", (0, 0, 200, 200))))
        row = self.row("WeedNet-R/dataset/JPEGImages/1.jpg", "weednetr", "train/Plant/WeedNet-R_1_01.jpg")
        with AnnotationReader(self.source, archives=[archive], aliases=["WeedNet-R/dataset/Annotations=archive-root"]) as reader:
            recipe = RecipeDeriver(reader).derive(row)
        self.assertEqual(recipe["bbox_right"], "200")

    def test_legacy_jpeg_roundtrip_is_included(self):
        path = self.make_image("Weed25/bidens/a.png", (512, 512))
        image = Image.open(path)
        self.addCleanup(image.close)
        recipe = {"bbox_left": "0", "bbox_top": "0", "bbox_right": "200", "bbox_bottom": "200",
                  "intermediate_mode": "preserve", "recipe_id": "s1"}
        row = self.row("Weed25/bidens/a.png", "weed25", "train/Plant/Weed25_a_01.jpg", recipe_id="s1")
        encoded = encoded_crop(image, recipe)
        self.assertEqual(encoded[:2], b"\xff\xd8")
        with Image.open(io.BytesIO(encoded)) as decoded:
            expected = resize_rgb_png(decoded)
        self.assertEqual(render_sample(row, path, recipe), expected)


if __name__ == "__main__":
    unittest.main()
