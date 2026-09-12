"""Portable, epoch-resumable CNN/ViT training for the released OpenPlant splits."""
from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from .train_utils import (boolean, choose_device, config_dict, create_model, file_sha256,
                          load_checkpoint, load_config, make_dataset, make_loader,
                          read_classes, seed_everything, verify_manifest, write_json)


def run_epoch(model, loader, device, loss_fn, optimizer=None, scaler=None, clip_norm=1.0, amp=False):
    import torch
    training = optimizer is not None
    model.train(training)
    loss_sum, correct, count = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for inputs, targets in loader:
            inputs, targets = inputs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
            if training:
                optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, enabled=amp):
                logits = model(inputs)
                loss = loss_fn(logits, targets)
            if not torch.isfinite(loss):
                raise FloatingPointError("Non-finite loss; checkpoint was not advanced")
            if training:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                if clip_norm > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), clip_norm)
                scaler.step(optimizer)
                scaler.update()
            count += targets.numel()
            loss_sum += loss.item() * targets.numel()
            correct += int((logits.argmax(1) == targets).sum().item())
    return {"loss": loss_sum / count, "accuracy": correct / count, "samples": count}


def _rng_state():
    import numpy as np
    import torch
    state = np.random.get_state()
    return {"python": random.getstate(), "numpy": [state[0], state[1].tolist(), *state[2:]],
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}


def _restore_rng(state):
    import numpy as np
    import torch
    random.setstate(state["python"])
    saved = state["numpy"]
    np.random.set_state((saved[0], np.array(saved[1], dtype=np.uint32), *saved[2:]))
    torch.set_rng_state(state["torch"])
    if state["cuda"] and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])


def _save_checkpoint(path, checkpoint):
    import torch
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(checkpoint, temporary)
    temporary.replace(path)


def _reconcile_resume(output, checkpoint):
    """Recover the two-file commit if execution stopped between best.pt and last.pt."""
    import torch
    best_path = Path(output) / "best.pt"
    best = torch.load(best_path, map_location="cpu", weights_only=True) if best_path.exists() else None
    if best is not None:
        if not isinstance(best, dict) or best.get("format_version") != 1:
            raise ValueError("best.pt is not a complete release checkpoint")
        for key in ("class_names", "classes_sha256", "manifest_sha256"):
            if best.get(key) != checkpoint.get(key):
                raise ValueError(f"best.pt and resume checkpoint disagree on {key}")
        if best.get("epoch") != best.get("best_epoch"):
            raise ValueError("best.pt does not contain its declared best epoch")
        if best["epoch"] > checkpoint["epoch"]:
            # best.pt is a complete training snapshot, so the interrupted epoch need not be replayed.
            # Confirm it belongs to the same history before promoting it to last.pt.
            old_config = {k: v for k, v in checkpoint["config"].items() if k != "epochs"}
            new_config = {k: v for k, v in best["config"].items() if k != "epochs"}
            if best.get("history", [])[:len(checkpoint["history"])] != checkpoint["history"] or old_config != new_config:
                raise ValueError("Newer best.pt is not a continuation of the resume checkpoint")
            _save_checkpoint(Path(output) / "last.pt", best)
            print(f"Recovered completed epoch {best['epoch']} from best.pt after an interrupted checkpoint commit", flush=True)
            return best
        if best["best_epoch"] == checkpoint["best_epoch"] and best.get("best_val_loss") == checkpoint["best_val_loss"]:
            return checkpoint
    # Also recover a missing first best or files produced by the previous last-before-best order.
    if checkpoint["epoch"] == checkpoint["best_epoch"]:
        _save_checkpoint(best_path, checkpoint)
        print(f"Restored best.pt from resume checkpoint at epoch {checkpoint['epoch']}", flush=True)
        return checkpoint
    raise ValueError("best.pt is missing or inconsistent and its historical weights cannot be recovered from last.pt; "
                     "restore the matching best.pt, or use --weights in a new output directory")


def train(args):
    import torch
    import torchvision
    import timm
    config = load_config(args.config)
    for name in ("seed", "workers", "batch_size", "epochs", "pretrained", "image_size", "amp", "data_parallel"):
        if getattr(args, name, None) is not None:
            setattr(config, name, getattr(args, name))
    config.validate()
    names, _ = read_classes(args.classes)
    if len(names) != config.num_classes:
        raise ValueError(f"Config has {config.num_classes} classes; classes.csv has {len(names)}")
    output = Path(args.output)
    if args.pretrained_file and (args.resume or args.weights):
        raise ValueError("--pretrained-file cannot be combined with --resume or --weights")
    if args.resume and output.resolve() != Path(args.resume).resolve().parent:
        raise ValueError("Resume into the original checkpoint directory to preserve best.pt and history")
    if output.exists() and any(output.iterdir()) and not args.resume:
        raise ValueError("Output directory is not empty; choose a new output or use --resume")
    device = choose_device(args.device)
    seed_everything(config.seed)
    train_set = make_dataset(args.data_root, "train", names, config, training=True)
    val_set = make_dataset(args.data_root, "val", names, config)
    if args.manifest:
        verify_manifest(train_set, args.manifest, "train", args.data_root)
        verify_manifest(val_set, args.manifest, "val", args.data_root)
    model = create_model(config, pretrained=config.pretrained and not (args.resume or args.weights),
                         pretrained_file=args.pretrained_file)
    checkpoint = None
    if args.resume or args.weights:
        checkpoint = load_checkpoint(args.resume or args.weights, model, names, resume=bool(args.resume))
    model = model.to(device)
    if config.data_parallel and device.type == "cuda" and torch.cuda.device_count() > 1:
        if device.index not in (None, 0):
            raise ValueError("DataParallel expects --device cuda or cuda:0; disable --data-parallel for another device")
        model = torch.nn.DataParallel(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=config.scheduler_gamma)
    amp = config.amp and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    start_epoch, best_loss, best_epoch, stale, history = 0, float("inf"), 0, 0, []
    if args.resume:
        for key in ("model_name", "num_classes", "image_size", "seed", "batch_size", "learning_rate",
                    "weight_decay", "scheduler_gamma", "mean", "std", "amp", "data_parallel", "workers"):
            old, new = checkpoint["config"][key], config_dict(config)[key]
            if isinstance(new, tuple):
                new = list(new)
            if isinstance(old, tuple):
                old = list(old)
            if old != new:
                raise ValueError(f"Resume config mismatch: {key}; use --weights for a new run")
        if checkpoint["classes_sha256"] != file_sha256(args.classes):
            raise ValueError("Class metadata has changed since checkpoint")
        manifest_hash = file_sha256(args.manifest) if args.manifest else None
        if checkpoint.get("manifest_sha256") != manifest_hash:
            raise ValueError("Manifest differs from the checkpoint")
        checkpoint = _reconcile_resume(output, checkpoint)
        bare_model = model.module if hasattr(model, "module") else model
        bare_model.load_state_dict(checkpoint["model_state"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        scheduler.load_state_dict(checkpoint["scheduler_state"])
        scaler.load_state_dict(checkpoint["scaler_state"])
        start_epoch, best_loss = checkpoint["epoch"], checkpoint["best_val_loss"]
        best_epoch, stale = checkpoint["best_epoch"], checkpoint["stale_epochs"]
        history = checkpoint["history"]
        _restore_rng(checkpoint["rng_state"])
    if start_epoch >= config.epochs:
        raise ValueError("Checkpoint already reached --epochs; increase the target epoch count")
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "config.json", config_dict(config))
    write_json(output / "environment.json", {"torch": str(torch.__version__), "torchvision": torchvision.__version__,
               "timm": timm.__version__, "device": str(device), "amp_enabled": amp,
               "classes_sha256": file_sha256(args.classes),
               "manifest_sha256": file_sha256(args.manifest) if args.manifest else None})
    loss_fn = torch.nn.CrossEntropyLoss()
    for epoch in range(start_epoch, config.epochs):
        begun = time.monotonic()
        lr = optimizer.param_groups[0]["lr"]
        training = run_epoch(model, make_loader(train_set, config, device, True, epoch), device,
                             loss_fn, optimizer, scaler, config.gradient_clip_norm, amp)
        validation = run_epoch(model, make_loader(val_set, config, device), device, loss_fn, amp=amp)
        scheduler.step()
        improved = validation["loss"] < best_loss
        if improved:
            best_loss, best_epoch, stale = validation["loss"], epoch + 1, 0
        else:
            stale += 1
        row = {"epoch": epoch + 1, "learning_rate": lr, "next_learning_rate": scheduler.get_last_lr()[0],
               "train": training, "val": validation, "seconds": time.monotonic() - begun}
        history.append(row)
        bare_model = model.module if hasattr(model, "module") else model
        saved = {"format_version": 1, "model_state": bare_model.state_dict(), "config": config_dict(config),
                 "class_names": names, "classes_sha256": file_sha256(args.classes),
                 "manifest_sha256": file_sha256(args.manifest) if args.manifest else None,
                 "optimizer_state": optimizer.state_dict(), "scheduler_state": scheduler.state_dict(),
                 "scaler_state": scaler.state_dict(), "rng_state": _rng_state(), "epoch": epoch + 1,
                 "best_val_loss": best_loss, "best_epoch": best_epoch, "stale_epochs": stale, "history": history}
        # Serialize immediately: a state_dict is a reference to live tensors until written.
        # Commit best first. A newer complete best.pt can recover an interrupted last.pt commit.
        for filename in (["best.pt", "last.pt"] if improved else ["last.pt"]):
            _save_checkpoint(output / filename, saved)
        write_json(output / "history.json", history)
        print(f"epoch={epoch + 1}/{config.epochs} train_loss={training['loss']:.5f} "
              f"val_loss={validation['loss']:.5f} val_accuracy={validation['accuracy']:.5f} "
              f"lr={lr:.6g} best_epoch={best_epoch}", flush=True)
        if config.patience and stale >= config.patience:
            print(f"Early stopping after {stale} epochs without lower validation loss", flush=True)
            break
    return output / "last.pt"


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, help="Root of prepared train/val/test image folders")
    parser.add_argument("--config", required=True, help="A configs/*.json model configuration")
    parser.add_argument("--classes", default="metadata/classes.csv")
    parser.add_argument("--manifest", help="Optional fixed manifest CSV[.gz]; checks exact split membership")
    parser.add_argument("--output", required=True, help="New output directory, or original directory for resume")
    parser.add_argument("--device", default="auto")
    for name in ("seed", "workers", "batch-size", "epochs", "image-size"):
        parser.add_argument("--" + name, type=int)
    for name in ("pretrained", "amp", "data-parallel"):
        parser.add_argument("--" + name, type=boolean)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--resume", help="Resume complete last.pt (includes optimizer, schedule and RNG state)")
    group.add_argument("--weights", help="Initialize from a legacy .pth or release .pt; start a fresh optimizer")
    parser.add_argument("--pretrained-file", help="Local timm pretraining checkpoint instead of a download")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        train(args)
    except (ValueError, FileNotFoundError, ImportError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
