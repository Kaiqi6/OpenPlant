"""Shared configuration, class-order, and checkpoint utilities (lazy ML imports)."""
from __future__ import annotations

import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass
class TrainConfig:
    model_name: str = "resnet18.a1_in1k"
    num_classes: int = 1167
    image_size: int = 224
    resize_shorter: int = 256
    batch_size: int = 64
    epochs: int = 100
    learning_rate: float = 0.001
    weight_decay: float = 0.1
    scheduler_gamma: float = 0.9
    gradient_clip_norm: float = 1.0
    seed: int = 42
    workers: int = 8
    amp: bool = True
    data_parallel: bool = True
    pretrained: bool = True
    patience: int = 0
    mean: tuple = (0.43056735, 0.46167394, 0.36951741)
    std: tuple = (0.22340974, 0.21595199, 0.22381605)
    provenance: dict | None = None

    def validate(self):
        for name in ("num_classes", "image_size", "resize_shorter", "batch_size", "epochs"):
            if not isinstance(getattr(self, name), int) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.workers < 0 or self.patience < 0:
            raise ValueError("workers and patience must be nonnegative")
        if self.learning_rate <= 0 or self.weight_decay < 0 or not 0 < self.scheduler_gamma <= 1:
            raise ValueError("Invalid optimizer or scheduler settings")
        if len(self.mean) != 3 or len(self.std) != 3 or any(v <= 0 for v in self.std):
            raise ValueError("RGB normalization requires three means and positive standard deviations")
        return self


def load_config(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    unknown = set(payload) - {f.name for f in fields(TrainConfig)}
    if unknown:
        raise ValueError(f"Unknown configuration fields: {sorted(unknown)}")
    return TrainConfig(**payload).validate()


def read_classes(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    names = [row["class_name"] for row in rows]
    ids = [int(row["class_id"]) for row in rows]
    if not names or ids != list(range(len(rows))):
        raise ValueError("classes.csv must have contiguous zero-based class_id in row order")
    if names != sorted(set(names)):
        raise ValueError("classes.csv names must be unique and sorted exactly as ImageFolder")
    return names, rows


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, payload):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def seed_everything(seed):
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def seed_worker(worker_id):
    import numpy as np
    import torch
    worker_seed = torch.initial_seed() % 2**32
    random.seed(worker_seed)
    np.random.seed(worker_seed)


def build_transform(config, training=False):
    from torchvision import transforms
    # The input root contains the fixed-shorter-edge-256 images built by the data pipeline.
    # Do not resize again: a second JPEG resize/re-encode would change historical inputs.
    operations = ([transforms.RandomResizedCrop(config.image_size),
                   transforms.RandomHorizontalFlip(), transforms.RandomRotation(15),
                   transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2)]
                  if training else [transforms.CenterCrop(config.image_size)])
    return transforms.Compose(operations + [transforms.ToTensor(), transforms.Normalize(config.mean, config.std)])


def make_dataset(root, split, class_names, config, training=False):
    from torchvision.datasets import ImageFolder
    dataset = ImageFolder(Path(root) / split, transform=build_transform(config, training), allow_empty=True)
    if dataset.classes != class_names:
        missing = sorted(set(class_names) - set(dataset.classes))
        extra = sorted(set(dataset.classes) - set(class_names))
        raise ValueError(f"{split} class order differs from classes.csv; missing={missing[:8]}, extra={extra[:8]}")
    if not dataset.samples:
        raise ValueError(f"Empty split: {split}")
    return dataset


def make_loader(dataset, config, device, training=False, epoch=0):
    import torch
    options = dict(batch_size=config.batch_size, num_workers=config.workers,
                   shuffle=training, pin_memory=device.type == "cuda", worker_init_fn=seed_worker,
                   generator=torch.Generator().manual_seed(config.seed + epoch))
    if config.workers:
        # Workers restart per epoch; a resumed epoch receives the same worker seeds.
        options.update(persistent_workers=False, prefetch_factor=2)
    return torch.utils.data.DataLoader(dataset, **options)


def verify_manifest(dataset, manifest_path, split, data_root):
    """Check exact file membership and labels; image-byte checks belong to data audit."""
    import gzip
    root = Path(data_root).resolve()
    observed = {Path(path).resolve().relative_to(root).as_posix(): label for path, label in dataset.samples}
    opener = gzip.open if str(manifest_path).endswith(".gz") else open
    expected = {}
    with opener(manifest_path, "rt", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["split"] == split:
                path = row["image_path"].replace("\\", "/")
                if path in expected:
                    raise ValueError(f"Duplicate manifest image_path: {path}")
                expected[path] = int(row["class_id"])
    if observed != expected:
        raise ValueError(f"{split} differs from fixed manifest: files={len(observed)}, expected={len(expected)}, "
                         f"missing={len(expected.keys() - observed.keys())}, extra={len(observed.keys() - expected.keys())}")


def create_model(config, pretrained=False, pretrained_file=None):
    import timm
    registered = timm.models.get_pretrained_cfg(config.model_name)
    if registered is not None and registered.fixed_input_size:
        native_size = tuple(registered.input_size[-2:])
        if native_size != (config.image_size, config.image_size):
            raise ValueError(f"{config.model_name} requires its fixed input size {native_size}; "
                             f"--image-size {config.image_size} only changes transforms. "
                             "Use the model's native configuration or a model with flexible input size")
    kwargs = dict(pretrained=pretrained, num_classes=config.num_classes)
    if pretrained_file:
        if not pretrained:
            raise ValueError("--pretrained-file requires --pretrained true")
        kwargs["pretrained_cfg_overlay"] = {"file": str(pretrained_file)}
    return timm.create_model(config.model_name, **kwargs)


def load_checkpoint(path, model, class_names, *, resume=False):
    """Accept tensor-only legacy state_dict files and this release's checkpoint schema."""
    import torch
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict):
        raise ValueError("Expected a state_dict or a structured OpenPlant checkpoint")
    state = checkpoint.get("model_state", checkpoint.get("state_dict", checkpoint))
    saved_classes = checkpoint.get("class_names")
    if saved_classes is not None and saved_classes != class_names:
        raise ValueError("Checkpoint class order differs from classes.csv")
    if resume and checkpoint.get("format_version") != 1:
        raise ValueError("--resume requires a complete release checkpoint; use --weights to initialize legacy weights")
    if not isinstance(state, dict) or not all(isinstance(k, str) and torch.is_tensor(v) for k, v in state.items()):
        raise ValueError("Checkpoint model state must contain only named tensors")
    state = {key[7:] if key.startswith("module.") else key: value for key, value in state.items()}
    expected = model.state_dict()
    mismatches = [f"{key}: {tuple(value.shape)} != {tuple(expected[key].shape)}"
                  for key, value in state.items() if key in expected and value.shape != expected[key].shape]
    if mismatches:
        raise ValueError("Checkpoint/model shape mismatch (check model and class count): " + "; ".join(mismatches[:5]))
    model.load_state_dict(state, strict=True)
    return checkpoint


def choose_device(value):
    import torch
    if value == "auto":
        value = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(value)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but unavailable; use --device cpu")
    return device


def boolean(value):
    import argparse
    if isinstance(value, bool):
        return value
    if value.lower() in ("true", "1", "yes"):
        return True
    if value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError("Expected true or false")


def config_dict(config):
    return asdict(config)
