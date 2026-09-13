# Training and evaluation

Train and evaluate OpenPlant's 16 CNN/ViT baselines using the fixed data splits and per-model JSON configurations.

## Install

Use Python 3.10 or later in a virtual environment. Install a matching PyTorch/torchvision pair for your CPU or CUDA platform, then:

```bash
python -m pip install -r requirements-train.txt
```

The requirements pin `timm 1.0.20`, the version reported in the paper.

## Fixed data and class order

Obtain the source images under their licenses and follow the [reconstruction guide](reconstruction.md) to prepare:

```text
prepared/
  train/<class_name>/<image>.png
  val/<class_name>/<image>.png
  test/<class_name>/<image>.png
```

`metadata/manifest.csv.gz` fixes image membership and split assignments. `metadata/classes.csv` defines 0-based class IDs in ImageFolder's lexicographic order. All splits must contain the same class directories, including empty ones for zero-count classes. Passing `--manifest` checks the exact paths and labels against the published mapping. These checks do not verify image bytes; blank hashes and byte counts in the manifest were not recorded in the historical workbook.

Inputs are RGB images with the shorter edge resized to 256 pixels, preserving aspect ratio. Training applies `RandomResizedCrop`, horizontal flip (p=0.5), rotation (±15°), brightness/contrast/saturation jitter (0.2), tensor conversion and normalization. Validation and test use `CenterCrop` and the same normalization. Interpolation follows torchvision defaults: bilinear for random resized crop, nearest for rotation.

```text
mean = [0.43056735, 0.46167394, 0.36951741]
std  = [0.22340974, 0.21595199, 0.22381605]
```

## Run a model

Run from the repository root after preparing the images:

```bash
python scripts/train.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --output runs/resnet18 --device cuda
python scripts/evaluate.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights runs/resnet18/best.pt --output runs/resnet18-test --device cuda
```

Pretraining uses timm's configured weights. Add `--pretrained-file /path/to/weights.bin` to load a local file. For CPU training from random initialization, use `--device cpu --workers 0 --pretrained false --amp false --data-parallel false`.

To evaluate a published checkpoint:

```bash
python scripts/evaluate.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights model/resnet18.pth --output runs/published-resnet18 --device cuda
```

The loader accepts original `.pth` state dictionaries, including `module.` prefixes, and new complete checkpoints. It uses `weights_only=True` and rejects incompatible parameter shapes. The original 1,167-class weights depend on the published class order; new checkpoints also store class names and the metadata hash.

Training saves `best.pt` at the lowest validation loss and `last.pt` after every completed epoch, alongside `history.json`, `config.json` and `environment.json`. Full checkpoints include optimizer, scheduler, AMP scaler and random-number states. Resume in the same output directory:

```bash
python scripts/train.py --data-root /path/to/prepared --config configs/resnet18.json --manifest metadata/manifest.csv.gz --output runs/resnet18 --resume runs/resnet18/last.pt --epochs 100 --device cuda
```

`--epochs` sets the final epoch count. Files are replaced atomically, with an improved `best.pt` written before `last.pt`. Resume recovers a newer complete best checkpoint if writing stopped between the two files. It can also restore a missing best file when `last.pt` contains that epoch; otherwise it reports an error. If the first epoch saved only `best.pt`, resume from that file.

Use `--weights model/resnet18.pth` to start a new run from legacy weights. CLI overrides include `--seed`, `--workers`, `--batch-size`, `--epochs`, `--image-size`, `--amp`, `--data-parallel` and `--pretrained`. Fixed-input models such as ViT and Swin reject non-native image sizes; flexible models such as ResNet accept them. Copy the JSON to change other settings. Changing the seed never changes the fixed splits.

## Models and historical settings

All configurations use AdamW, weight decay 0.1, cross-entropy loss, gradient clipping at norm 1.0 and exponential learning-rate decay (`gamma=0.9` after each epoch). Training lasts 100 epochs with early stopping disabled (`patience=0`).

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

Fourteen saved run configurations specify batch size 64, seed 42, eight workers, AMP and DataParallel enabled, and learning rate 0.001.

\* ViT-Base and EfficientViT-L3 have empty saved configuration files. Their 100 recorded learning rates start at 0.009 after decay by 0.9, implying an initial rate of 0.01. Their remaining settings fall back to `test11.py`: batch size 64, seed 42, 16 workers, AMP enabled and DataParallel disabled. These are defaults, not recovered runtime values. Each JSON's `provenance` field records the evidence and fallback settings.

Crop sizes follow timm's registered pretrained configurations. Xception retains the historical 299-pixel center crop on images with shorter edge 256, padding where needed. The untagged ViT-Tiny name retains timm's default `augreg_in21k_ft_in1k` initialization.

## Evaluation outputs and definitions

| File | Contents |
|---|---|
| `metrics.json` | Top-1/top-5 accuracy, cross-entropy, Cohen's kappa, precision/recall/F1 and ranking metrics |
| `per_class.csv` | Precision, recall, F1, support, AP and PR-AUC by class |
| `predictions.csv` | Relative image path, true/predicted labels and top-5 labels/probabilities |
| `confusion_matrix.npy` | Counts indexed by the published class IDs |

Precision, recall and F1 use macro, weighted and micro averaging over all classes; undefined precision/recall is zero. AP uses `average_precision_score`; PR-AUC integrates the precision-recall curve with trapezoids. Macro ranking averages classes with evaluation positives; micro ranking flattens all sample/class pairs. Undefined kappa is `null`. Top-k uses `min(5, number_of_classes)` and records the actual `top_k`.

With `total_count` in `classes.csv`, evaluation also reports head/medium/tail accuracy. Classes are ranked by total image count, with class ID breaking ties: the first floor(20%) are head, the next through floor(50%) are medium, and the remainder are tail. OpenPlant has 233/350/584 classes in these groups; memberships are saved in the output.

`--ranking-metrics full` computes macro and micro AP/PR-AUC. Exact micro ranking needs several gigabytes of RAM for the full test set. Use `--ranking-metrics macro` to skip micro ranking or `--ranking-metrics none` for classification metrics alone. Add `--save-probabilities` to retain the float32 `probabilities.npy` array.

## Reproduction scope and validation

Use the fixed mapping and original weights when comparing with the paper. The rewritten trainer unscales AMP gradients before clipping, keeps the scaler and scheduler across epochs, and saves the best weights immediately. The original scripts retained live `state_dict()` references until serialization, so their `best` filenames do not establish the lowest-loss epoch. These corrections, the two fallback configurations and runtime versions can change scores; the full 16-model benchmark has not been rerun with this code.

Run the synthetic CPU tests:

```bash
python -m unittest discover -s tests -p test_training.py -v
```

Four tests cover training/resume equivalence, interrupted checkpoint recovery, evaluation exports, manifest and model-shape checks. They passed with PyTorch 2.4.0, torchvision 0.19.0 and timm 1.0.20. All 16 model configurations resolve, and the original ResNet-18 weights load strictly.

## VLM scope

The paper's 12-VLM study uses a separate multiple-choice protocol with candidate labels derived from CNN/ViT predictions. This release provides CNN/ViT training and prediction exports. VLM inference backends and the multiple-choice evaluation pipeline are not included.
