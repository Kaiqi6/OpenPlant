"""Small synthetic checks; no OpenPlant images or downloaded weights are used."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from openplant.train_utils import TrainConfig, config_dict, read_classes


ML_AVAILABLE = all(importlib.util.find_spec(name) for name in ("torch", "torchvision", "timm", "sklearn"))


class ClassOrderTests(unittest.TestCase):
    def test_rejects_unsorted_classes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "classes.csv"
            path.write_text("class_id,class_name\n0,Zea mays\n1,Abutilon theophrasti\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sorted"):
                read_classes(path)


@unittest.skipUnless(ML_AVAILABLE, "training dependencies are not installed")
class TrainingSmokeTests(unittest.TestCase):
    def test_fixed_input_models_reject_transform_only_size_override(self):
        from openplant.train_utils import create_model
        for name in ("vit_tiny_patch16_224", "swinv2_tiny_window8_256.ms_in1k"):
            with self.subTest(model=name):
                config = TrainConfig(model_name=name, image_size=32, pretrained=False)
                with self.assertRaisesRegex(ValueError, "fixed input size"):
                    create_model(config, pretrained=False)

    def test_resume_recovers_interrupted_checkpoint_pair(self):
        import torch
        from openplant.training import _reconcile_resume
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = {"format_version": 1, "epoch": 1, "best_epoch": 1, "best_val_loss": 0.9,
                   "class_names": ["A", "B"], "classes_sha256": "fixed", "manifest_sha256": "fixed",
                   "config": {"epochs": 3, "seed": 42}, "history": [{"epoch": 1, "val_loss": 0.9}],
                   "model_state": {"weight": torch.tensor([1.0])}, "optimizer_state": {"step": 1}}
            newer = dict(old, epoch=2, best_epoch=2, best_val_loss=0.4,
                         history=old["history"] + [{"epoch": 2, "val_loss": 0.4}],
                         model_state={"weight": torch.tensor([2.0])}, optimizer_state={"step": 2})
            # Emulate a real process interruption: new best was committed, last still references epoch 1.
            torch.save(old, root / "last.pt")
            torch.save(newer, root / "best.pt")
            recovered = _reconcile_resume(root, torch.load(root / "last.pt", weights_only=True))
            self.assertEqual(recovered["epoch"], 2)
            self.assertEqual(recovered["optimizer_state"]["step"], 2)
            on_disk = torch.load(root / "last.pt", weights_only=True)
            self.assertTrue(torch.equal(on_disk["model_state"]["weight"], torch.tensor([2.0])))
            # Missing best is repairable when last itself contains the best weights.
            (root / "best.pt").unlink()
            _reconcile_resume(root, on_disk)
            self.assertEqual(torch.load(root / "best.pt", weights_only=True)["epoch"], 2)
            # An older best that is absent cannot be reconstructed from later, worse weights.
            (root / "best.pt").unlink()
            worse = dict(newer, epoch=3, model_state={"weight": torch.tensor([3.0])})
            with self.assertRaisesRegex(ValueError, "cannot be recovered"):
                _reconcile_resume(root, worse)

    def test_cpu_train_resume_evaluate_and_legacy_validation(self):
        import numpy as np
        import torch
        from PIL import Image
        from openplant.training import build_parser as train_parser, train
        from openplant.evaluation import build_parser as eval_parser, evaluate, ranking_metrics
        from openplant.train_utils import create_model, load_checkpoint, make_dataset, verify_manifest

        torch.set_num_threads(2)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            names = ["Abutilon theophrasti", "Zea mays"]
            class_path = root / "classes.csv"
            class_path.write_text("class_id,class_name,total_count\n0,Abutilon theophrasti,6\n1,Zea mays,6\n", encoding="utf-8")
            rows = []
            for split in ("train", "val", "test"):
                for label, name in enumerate(names):
                    (root / "images" / split / name).mkdir(parents=True)
                    for index in range(2):
                        image_path = f"{split}/{name}/{index}.png"
                        color = (40 + 80 * label, 100 + index * 50, 80)
                        Image.new("RGB", (40, 48), color).save(root / "images" / image_path)
                        rows.append({"image_path": image_path, "class_id": label, "split": split})
            manifest = root / "manifest.csv"
            with manifest.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["image_path", "class_id", "split"])
                writer.writeheader()
                writer.writerows(rows)
            config = TrainConfig(num_classes=2, image_size=32, batch_size=2, workers=0,
                                 epochs=1, pretrained=False, amp=False, data_parallel=False)
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config_dict(config)), encoding="utf-8")
            run = root / "run"
            base = ["--config", str(config_path), "--classes", str(class_path), "--data-root", str(root / "images"),
                    "--manifest", str(manifest), "--device", "cpu"]
            train(train_parser().parse_args(base + ["--output", str(run), "--pretrained", "false"]))
            first = torch.load(run / "best.pt", map_location="cpu", weights_only=True)
            self.assertEqual(first["epoch"], 1)
            self.assertAlmostEqual(first["scheduler_state"]["_last_lr"][0], 0.0009)
            train(train_parser().parse_args(base + ["--output", str(run), "--resume", str(run / "last.pt"), "--epochs", "2"]))
            resumed = torch.load(run / "last.pt", map_location="cpu", weights_only=True)
            self.assertEqual(resumed["epoch"], 2)
            self.assertEqual(len(resumed["history"]), 2)
            self.assertAlmostEqual(resumed["history"][1]["learning_rate"], 0.0009)
            continuous = root / "continuous"
            train(train_parser().parse_args(base + ["--output", str(continuous), "--epochs", "2"]))
            uninterrupted = torch.load(continuous / "last.pt", map_location="cpu", weights_only=True)
            for key in resumed["model_state"]:
                self.assertTrue(torch.equal(resumed["model_state"][key], uninterrupted["model_state"][key]), key)
            # This deterministic fixture worsens in epoch 2: best must remain an actual epoch-1 snapshot.
            if resumed["best_epoch"] == 1:
                best_again = torch.load(run / "best.pt", map_location="cpu", weights_only=True)
                self.assertEqual(best_again["epoch"], 1)
                for key in first["model_state"]:
                    self.assertTrue(torch.equal(first["model_state"][key], best_again["model_state"][key]))
            metrics = evaluate(eval_parser().parse_args(base + ["--weights", str(run / "best.pt"),
                               "--output", str(root / "evaluation"), "--ranking-metrics", "full"]))
            self.assertEqual(metrics["samples"], 4)
            self.assertEqual(metrics["top_k"], 2)
            self.assertEqual(metrics["top5_accuracy"], 1.0)
            self.assertTrue((root / "evaluation" / "predictions.csv").is_file())
            self.assertFalse((root / "evaluation" / "probabilities.npy").exists())
            model = create_model(config)
            legacy = root / "legacy.pth"
            torch.save({"module." + key: value for key, value in first["model_state"].items()}, legacy)
            load_checkpoint(legacy, model, names)
            with self.assertRaisesRegex(ValueError, "complete release checkpoint"):
                load_checkpoint(legacy, model, names, resume=True)
            invalid = dict(first["model_state"])
            invalid["fc.weight"] = torch.zeros((3, 512))
            torch.save(invalid, legacy)
            with self.assertRaisesRegex(ValueError, "shape mismatch"):
                load_checkpoint(legacy, model, names)
            dataset = make_dataset(root / "images", "test", names, config)
            verify_manifest(dataset, manifest, "test", root / "images")
            manifest.write_text("image_path,class_id,split\ntest/extra.png,0,test\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fixed manifest"):
                verify_manifest(dataset, manifest, "test", root / "images")
            perfect, _, _ = ranking_metrics(np.array([0, 1]), np.array([[0.9, 0.1], [0.1, 0.9]]))
            self.assertEqual(perfect["micro_ap"], 1.0)
            self.assertEqual(perfect["macro_ap"], 1.0)


if __name__ == "__main__":
    unittest.main()
