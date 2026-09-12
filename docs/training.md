# Training and evaluation

This release provides rewritten training and evaluation programs for all 16 CNN/ViT baselines. The model names, data normalization, augmentations and available historical settings are recorded in versioned JSON configurations. The original project scripts and published model files are preserved; this release does not retrain the paper's experiments.

## Install

Use a virtual environment with Python 3.10 or later. Install a matching PyTorch/torchvision pair for your CPU or CUDA platform, then install:

```bash
python -m pip install -r requirements-train.txt
```

The paper reports `timm 1.0.20`, which is pinned here. PyTorch and torchvision must be compatible with each other and with the local accelerator. No OpenPlant images, ImageNet weights or commercial API calls are needed for `--help` or the synthetic smoke test.

## Fixed data and class order

Use the prepared image tree produced by the reconstruction pipeline:

```text
prepared/
  train/<class_name>/<image>.png
  val/<class_name>/<image>.png
  test/<class_name>/<image>.png
```

`metadata/manifest.csv.gz` fixes image membership and train/validation/test assignments. `metadata/classes.csv` fixes 0-based class IDs in the lexicographic order used by ImageFolder. Every split must expose the same class directories, including empty directories for any zero-count class. The code rejects missing, extra or reordered classes. Passing `--manifest` also rejects different files or labels. It never creates a new random split.

The manifest was exported from the historical mapping workbook. Image hashes and byte counts that were not present in that record are blank. The release preparation did not scan or validate the original image files; the published mapping is the source of the fixed membership. Membership checks in the training commands compare paths and class IDs, not image bytes. Use the data audit command when checking a locally reconstructed copy.

Inputs must already follow the published image preparation recipe: RGB, shorter edge 256 pixels with aspect ratio preserved. The training code does not resize them a second time. Training applies `RandomResizedCrop`, horizontal flip (p=0.5), rotation (±15 degrees), brightness/contrast/saturation jitter (0.2), tensor conversion and normalization. Validation and test apply `CenterCrop`, tensor conversion and the same normalization. Torchvision's default interpolation is retained (bilinear for random resized crop, nearest for rotation).

Mean: `[0.43056735, 0.46167394, 0.36951741]`.
Standard deviation: `[0.22340974, 0.21595199, 0.22381605]`.

## Run a model

Run these commands from the repository root after preparing the images:

```bash
python scripts/train.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --output runs/resnet18 --device cuda
python scripts/evaluate.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights runs/resnet18/best.pt --output runs/resnet18-test --device cuda
```

The default pretrained initialization uses timm's configured weights. For a local pretraining file, add `--pretrained-file /path/to/weights.bin`. For a CPU run without any weight download, add `--device cpu --workers 0 --pretrained false --amp false --data-parallel false`. That is a randomly initialized experiment, so record it separately from pretrained baselines.

Evaluate an existing published OpenPlant checkpoint:

```bash
python scripts/evaluate.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights model/resnet18.pth --output runs/published-resnet18 --device cuda
```

The loader accepts the original tensor-only `OrderedDict` state files (including a leading `module.` prefix) and new complete checkpoints. It uses `torch.load(..., weights_only=True)`, strict parameter loading and shape checks. All 16 original checkpoints were inspected: their classification heads have 1,167 outputs. Legacy checkpoints do not embed class names, so their ordering depends on the released historical class mapping. New checkpoints store the full ordered class list and the metadata hash.

Training writes `best.pt` immediately whenever validation loss improves, `last.pt` after each completed epoch, `history.json`, the resolved `config.json` and `environment.json`. Each file is replaced atomically; an improved `best.pt` is committed before `last.pt`. Full checkpoints contain the optimizer, scheduler, AMP scaler and random-number states. Resume in the original output directory:

```bash
python scripts/train.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --output runs/resnet18 --resume runs/resnet18/last.pt --epochs 100 --device cuda
```

If a process stops between those two writes, resume detects a newer complete `best.pt` and continues from it, preserving both weights and optimizer state. A missing best file can be restored from `last.pt` when the last epoch is itself the best. An older best that is missing or inconsistent cannot be recovered from later weights, so resume fails with a clear error. If interruption occurred on the first epoch before `last.pt` was created, resume explicitly from `best.pt` instead.

`--epochs` is the final target epoch count. A legacy `.pth` has no complete optimizer or random-number state; use `--weights model/resnet18.pth` to initialize a new training run. `--seed`, `--workers`, `--batch-size`, `--epochs`, `--image-size`, `--amp`, `--data-parallel` and `--pretrained` override the JSON. `--image-size` supports models with flexible input dimensions, such as ResNet; fixed-input models such as ViT and Swin reject non-native dimensions before model creation. For other changes, copy the JSON to a new configuration. Seed changes affect training randomness and do not alter fixed data assignments.

## Models and historical settings

The common optimizer is AdamW with weight decay 0.1, cross-entropy loss and exponential learning-rate decay (`gamma=0.9`, once after each epoch). Training lasts 100 epochs. Early stopping is disabled (`patience=0`); the early-stopping script in the old project used an older 1,142-class dataset and is not the released baseline. Gradient clipping uses a maximum norm of 1.0.

| Configuration | timm model name | Crop size | Initial LR | Original checkpoint |
|---|---|---:|---:|---|
| `resnet18.json` | `resnet18.a1_in1k` | 224 | 0.001 | `model/resnet18.pth` |
| `resnet50.json` | `resnet50.a1_in1k` | 224 | 0.001 | `model/resnet50.pth` |
| `resnet101.json` | `resnet101.a1h_in1k` | 224 | 0.001 | `model/resnet101.pth` |
| `xception65p.json` | `xception65p.ra3_in1k` | 299 | 0.001 | `model/xception65p.pth` |
| `densenet121.json` | `densenet121.tv_in1k` | 224 | 0.001 | `model/densenet121.pth` |
| `efficientnet_b0.json` | `efficientnet_b0.ra_in1k` | 224 | 0.001 | `model/efficientnet_b0.pth` |
| `res2net50d.json` | `res2net50d.in1k` | 224 | 0.001 | `model/res2net50d.pth` |
| `resmlp24.json` | `resmlp_24_224.fb_in1k` | 224 | 0.001 | `model/resmlp24.pth` |
| `convnextv2_base.json` | `convnextv2_base.fcmae` | 224 | 0.001 | `model/convnextv2_base.pth` |
| `mobilenetv4.json` | `mobilenetv4_hybrid_medium.e500_r224_in1k` | 224 | 0.001 | `model/mobilenetv4.pth` |
| `vit_base.json` | `vit_base_patch16_224.mae` | 224 | 0.01* | `model/vit_base.pth` |
| `vit_tiny.json` | `vit_tiny_patch16_224` | 224 | 0.001 | `model/vit_tiny.pth` |
| `swinv2_base.json` | `swinv2_base_window8_256.ms_in1k` | 256 | 0.001 | `model/swinv2_base.pth` |
| `swinv2_tiny.json` | `swinv2_tiny_window8_256.ms_in1k` | 256 | 0.001 | `model/swinv2_tiny.pth` |
| `mobilevitv2.json` | `mobilevitv2_200.cvnets_in1k` | 256 | 0.001 | `model/mobilevitv2.pth` |
| `efficientvit_l3.json` | `efficientvit_l3.r224_in1k` | 224 | 0.01* | `model/efficientvit_l3.pth` |

Fourteen run folders contain saved configurations with batch size 64, seed 42, eight loader workers, AMP and DataParallel enabled, and learning rate 0.001. The ViT-Base and EfficientViT-L3 saved configuration files are empty. Their 100 recorded learning rates start at 0.009 after an epoch-end decay of 0.9, supporting the marked inference of an initial learning rate of 0.01. Batch size 64, seed 42, 16 workers, AMP enabled and DataParallel disabled for these two configurations are explicit fallbacks to the archived `test11.py` defaults, not recovered runtime settings. Each JSON contains `provenance` describing these distinctions and the historical run folder.

Image sizes follow the registered timm pretrained configurations, as the old scripts selected them from `model.default_cfg`. The historical transform for Xception applies a 299-pixel center crop to images with shorter edge 256; torchvision pads where required. This behavior is retained. The untagged ViT-Tiny name is retained from its run record; its registered default in the tested timm installation is `augreg_in21k_ft_in1k`.

## Evaluation outputs and definitions

`metrics.json` includes top-1 accuracy, top-5 accuracy, cross-entropy, Cohen's kappa and precision/recall/F1 using macro, weighted and micro averaging. All class IDs participate in those averages, with undefined precision/recall set to zero. `per_class.csv` contains class-level precision, recall, F1, support, AP and trapezoidal PR-AUC. `predictions.csv` records each relative image path, true and predicted labels and top-5 labels/probabilities. `confusion_matrix.npy` is indexed by the published class IDs.

AP and PR-AUC are distinct: AP uses `average_precision_score`; PR-AUC integrates the precision-recall curve with trapezoids. Macro ranking metrics average classes with at least one evaluation positive. Micro ranking metrics flatten all sample/class pairs. Undefined kappa is exported as JSON `null`. When fewer than five classes are used in a smoke fixture, top-k uses `min(5, number_of_classes)` and exports the actual `top_k`.

If `classes.csv` includes `total_count`, accuracy is also reported for frequency groups ranked by total image count, with class ID as a deterministic tie break. The first floor(20%) are head classes, the next through floor(50%) are medium classes and the remainder are tail classes. For OpenPlant this gives 233/350/584 classes. The group memberships are saved explicitly; no assumption is made that ties were handled identically in every historical plotting script.

The default `--ranking-metrics full` computes exact macro and micro AP/PR-AUC. Scores are written through a float32 memory-mapped array to reduce inference memory. Exact micro sorting still needs several gigabytes of RAM for the full test set because it operates on `number_of_images × 1167` entries. Use `--ranking-metrics macro` to omit micro ranking, or `--ranking-metrics none` for classification-only evaluation. Skipped metrics are omitted. The temporary probability array is removed at completion unless `--save-probabilities` is supplied.

## Reproduction scope and validation

The rewritten programs preserve the documented data protocol and recovered model settings. They correct implementation issues in the archived scripts: AMP gradients are unscaled before clipping; the scaler and scheduler persist across epochs; DataParallel is configured once; CPU and zero-worker execution are supported; the best validation-loss checkpoint is serialized immediately; and complete state is available for epoch-boundary resume. Original `best_model_state = model.state_dict()` assignments retained references to live tensors until final serialization, so historical filenames alone do not establish that a saved file is the lowest-loss epoch. The new evaluation also computes softmax in float32 after model inference.

Those corrections, the two partially recovered configurations, library/backend versions and numerical precision can change results. This release does not claim that rerunning the rewritten code produces the paper's exact numerical scores. The historical fixed mapping and original model weights remain the reference for comparison. Neither the original image bytes nor the full 16-model experiment was revalidated during this release.

Run the synthetic test:

```bash
python -m unittest discover -s tests -p test_training.py -v
```

It generates a temporary two-class image fixture and checks CPU training without downloads, equality of continuous and resumed training weights, interrupted best/last checkpoint recovery, stable best-checkpoint storage, evaluation and CSV exports, fixed-manifest mismatch detection, safe legacy checkpoint loading, rejection of incompatible classification heads and fixed-input dimensions, and binary AP calculations. All four training tests passed with PyTorch 2.4.0 and torchvision 0.19.0, both with the available timm 1.0.8 environment and with an isolated local installation of the pinned timm 1.0.20. The pinned version also resolved all 16 model configurations and strictly loaded the original ResNet-18 checkpoint. Full-dataset and all-model experiment validation remain outside this release check.

## VLM scope

The runnable baseline pipeline in this release covers the 16 CNN/ViT models. The paper's 12-VLM study used a separate multiple-choice protocol with candidate labels derived from CNN/ViT predictions and API or local model backends. Commercial credentials and personal inference scripts are not included. CNN/ViT prediction exports can support a future audited VLM evaluation release; they are not themselves a reproduction of the paper's VLM results.
