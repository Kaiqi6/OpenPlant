"""Evaluate fixed OpenPlant splits and export metrics and per-image predictions."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from .train_utils import (boolean, choose_device, create_model, file_sha256, load_checkpoint,
                          load_config, make_dataset, make_loader, read_classes,
                          verify_manifest, write_json)


def classification_metrics(labels, predictions, num_classes):
    import numpy as np
    from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support
    labels, predictions = np.asarray(labels), np.asarray(predictions)
    per_class = precision_recall_fscore_support(labels, predictions, labels=np.arange(num_classes), zero_division=0)
    results = {"accuracy": float(np.mean(labels == predictions)), "samples": int(len(labels))}
    for average in ("macro", "weighted", "micro"):
        p, r, f, _ = precision_recall_fscore_support(labels, predictions, labels=np.arange(num_classes),
                                                   average=average, zero_division=0)
        results.update({f"precision_{average}": float(p), f"recall_{average}": float(r), f"f1_{average}": float(f)})
    kappa = float(cohen_kappa_score(labels, predictions, labels=np.arange(num_classes)))
    results["cohen_kappa"] = kappa if math.isfinite(kappa) else None
    return results, per_class


def ranking_metrics(labels, probabilities, mode="full"):
    """Match the original one-vs-rest AP and trapezoidal PR-AUC definitions."""
    import numpy as np
    from sklearn.metrics import average_precision_score, precision_recall_curve, auc
    labels = np.asarray(labels)
    aps, pr_aucs = [], []
    for column in range(probabilities.shape[1]):
        binary = labels == column
        if not binary.any():
            aps.append(None)
            pr_aucs.append(None)
            continue
        precision, recall, _ = precision_recall_curve(binary, probabilities[:, column])
        aps.append(float(average_precision_score(binary, probabilities[:, column])))
        pr_aucs.append(float(auc(recall, precision)))
    results = {"macro_ap": float(np.mean([x for x in aps if x is not None])),
               "macro_pr_auc": float(np.mean([x for x in pr_aucs if x is not None])),
               "ranking_macro_policy": "mean over classes with at least one evaluation positive"}
    if mode == "full":
        # sklearn's exact micro ranking sorts N*C scores; see docs/training.md for RAM cost.
        binary = np.zeros(probabilities.shape, dtype=np.uint8)
        binary[np.arange(len(labels)), labels] = 1
        precision, recall, _ = precision_recall_curve(binary.ravel(), probabilities.ravel())
        results["micro_pr_auc"] = float(auc(recall, precision))
        results["micro_ap"] = float(average_precision_score(binary.ravel(), probabilities.ravel()))
    return results, aps, pr_aucs


def frequency_group_metrics(labels, predictions, class_rows):
    """Rank by total published image counts; preserve explicit, reproducible tie breaks."""
    import numpy as np
    if not class_rows or any(not row.get("total_count") for row in class_rows):
        return {}
    order = sorted(range(len(class_rows)), key=lambda index: (-int(class_rows[index]["total_count"]), index))
    head_end, medium_end = int(len(order) * 0.2), int(len(order) * 0.5)
    groups = {"head": order[:head_end], "medium": order[head_end:medium_end], "tail": order[medium_end:]}
    labels, predictions = np.asarray(labels), np.asarray(predictions)
    result = {}
    for name, ids in groups.items():
        mask = np.isin(labels, ids)
        result[name] = {"class_count": len(ids), "samples": int(mask.sum()),
                        "accuracy": float(np.mean(labels[mask] == predictions[mask])) if mask.any() else None,
                        "class_ids": ids}
    return result


def evaluate(args):
    import numpy as np
    import torch
    from sklearn.metrics import confusion_matrix
    config = load_config(args.config)
    for key in ("batch_size", "workers", "image_size", "amp"):
        if getattr(args, key, None) is not None:
            setattr(config, key, getattr(args, key))
    config.validate()
    names, class_rows = read_classes(args.classes)
    if len(names) != config.num_classes:
        raise ValueError("Config class count differs from classes.csv")
    output = Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Evaluation output directory is not empty; choose a new directory")
    device = choose_device(args.device)
    dataset = make_dataset(args.data_root, args.split, names, config)
    if args.manifest:
        verify_manifest(dataset, args.manifest, args.split, args.data_root)
    # Evaluation never needs an ImageNet download: all model weights come from --weights.
    model = create_model(config, pretrained=False)
    checkpoint = load_checkpoint(args.weights, model, names)
    saved_config = checkpoint.get("config")
    if saved_config:
        for key in ("model_name", "num_classes", "image_size", "mean", "std"):
            old, new = saved_config[key], getattr(config, key)
            if isinstance(old, (tuple, list)):
                old, new = list(old), list(new)
            if old != new:
                raise ValueError(f"Evaluation config differs from checkpoint: {key}")
    model.to(device).eval()
    output.mkdir(parents=True, exist_ok=True)
    count, classes = len(dataset), len(names)
    amp = config.amp and device.type == "cuda"
    labels = np.empty(count, dtype=np.int64)
    predictions = np.empty(count, dtype=np.int64)
    probabilities = None
    if args.ranking_metrics != "none" or args.save_probabilities:
        probabilities = np.lib.format.open_memmap(output / "probabilities.npy", mode="w+", dtype=np.float32,
                                                 shape=(count, classes))
    correct_topk, loss_sum, offset = 0, 0.0, 0
    top_k = min(5, classes)
    criterion = torch.nn.CrossEntropyLoss(reduction="sum")
    root = Path(args.data_root).resolve()
    with (output / "predictions.csv").open("w", encoding="utf-8", newline="") as handle, torch.inference_mode():
        writer = csv.writer(handle)
        writer.writerow(["image_path", "true_class_id", "true_class_name", "predicted_class_id",
                         "predicted_class_name", "top5_class_ids", "top5_probabilities"])
        for inputs, targets in make_loader(dataset, config, device):
            inputs = inputs.to(device, non_blocking=True)
            targets_device = targets.to(device, non_blocking=True)
            with torch.autocast(device_type=device.type, enabled=amp):
                logits = model(inputs)
                loss = criterion(logits, targets_device)
            probs = torch.softmax(logits.float(), dim=1)
            scores, indices = torch.topk(probs, k=top_k, dim=1)
            scores, indices = scores.cpu().numpy(), indices.cpu().numpy()
            actual, batch_count = targets.numpy(), targets.numel()
            labels[offset:offset + batch_count] = actual
            predictions[offset:offset + batch_count] = indices[:, 0]
            if probabilities is not None:
                probabilities[offset:offset + batch_count] = probs.cpu().numpy()
            correct_topk += int((indices == actual[:, None]).any(axis=1).sum())
            loss_sum += loss.item()
            for index in range(batch_count):
                image_path = Path(dataset.samples[offset + index][0]).resolve().relative_to(root).as_posix()
                truth, predicted = int(actual[index]), int(indices[index, 0])
                writer.writerow([image_path, truth, names[truth], predicted, names[predicted],
                                 json.dumps(indices[index].tolist()), json.dumps(scores[index].tolist())])
            offset += batch_count
    results, per_class = classification_metrics(labels, predictions, classes)
    results.update({"top5_accuracy": correct_topk / count, "top_k": top_k, "cross_entropy": loss_sum / count,
                    "model_name": config.model_name, "split": args.split, "amp_enabled": amp,
                    "ranking_metrics": args.ranking_metrics, "classes_sha256": file_sha256(args.classes),
                    "checkpoint_sha256": file_sha256(args.weights),
                    "manifest_sha256": file_sha256(args.manifest) if args.manifest else None})
    aps, pr_aucs = [None] * classes, [None] * classes
    if args.ranking_metrics != "none":
        probabilities.flush()
        ranking, aps, pr_aucs = ranking_metrics(labels, probabilities, args.ranking_metrics)
        results.update(ranking)
    group_results = frequency_group_metrics(labels, predictions, class_rows)
    if group_results:
        results["frequency_groups"] = group_results
        results["frequency_group_policy"] = "total_count descending, class_id ascending tie break; first floor(20%), then through floor(50%)"
    with (output / "per_class.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["class_id", "class_name", "precision", "recall", "f1", "support", "ap", "pr_auc"])
        for index, name in enumerate(names):
            writer.writerow([index, name, float(per_class[0][index]), float(per_class[1][index]),
                             float(per_class[2][index]), int(per_class[3][index]), aps[index], pr_aucs[index]])
    np.save(output / "confusion_matrix.npy", confusion_matrix(labels, predictions, labels=np.arange(classes)))
    write_json(output / "metrics.json", results)
    if probabilities is not None:
        probabilities.flush()
        del probabilities
        if not args.save_probabilities:
            (output / "probabilities.npy").unlink()
    print(json.dumps({key: value for key, value in results.items() if key != "frequency_groups"}, indent=2))
    return results


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--classes", default="metadata/classes.csv")
    parser.add_argument("--manifest", help="Fixed manifest CSV[.gz] for exact membership checks")
    parser.add_argument("--weights", required=True, help="Legacy model/*.pth or new best.pt/last.pt")
    parser.add_argument("--output", required=True)
    parser.add_argument("--split", choices=("train", "val", "test"), default="test")
    parser.add_argument("--device", default="auto")
    for name in ("batch-size", "workers", "image-size"):
        parser.add_argument("--" + name, type=int)
    parser.add_argument("--amp", type=boolean)
    parser.add_argument("--ranking-metrics", choices=("none", "macro", "full"), default="full",
                        help="full: exact per-class and micro AP/PR-AUC; large datasets need substantial RAM")
    parser.add_argument("--save-probabilities", action="store_true", help="Retain float32 probabilities.npy")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        evaluate(args)
    except (ValueError, FileNotFoundError, ImportError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
