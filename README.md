# OpenPlant

**A large-scale benchmark for agricultural plant classification**

[Paper](https://doi.org/10.3390/plants15050727) · [Image manifest](metadata/manifest.csv.gz) · [41 source datasets](docs/sources.md) · [Reconstruction](docs/reconstruction.md) · [Training](docs/training.md) · [Paper figures](docs/figures.md)

Official repository for **OpenPlant: A Large-Scale Benchmark Dataset for Agricultural Plant Classification Using CNNs, ViTs, and VLMs**, published in *Plants* 2026, 15(5), 727.

Kaiqi Liu, Wei Sun, Guanping Wang, Quan Feng, and Hui Li · Gansu Agricultural University

OpenPlant brings agricultural crops, weeds, and wild plants into a shared classification benchmark spanning diverse growth stages, plant structures, and environments. It contains **635,176 RGB images and 1,167 class labels**, with a long-tailed distribution. The paper evaluates **10 CNNs, 6 ViTs, and 12 vision-language models**.

![OpenPlant class distribution and representative head, medium, and tail samples](assets/figures/long_tail_distribution.png)

*Figure 1 from the paper: class distribution and representative samples.*

## What is available

This GitHub release provides the full image membership and fixed splits, source links and references, manifest-driven selection and reconstruction code, and training/evaluation programs for the 16 CNN/ViT baselines. The existing model checkpoints remain in [model/](model/). Obtain the underlying images from the [original data providers](docs/sources.md).

| Split | Images |
|---|---:|
| Training | 443,996 |
| Validation | 63,224 |
| Test | 127,956 |
| **Total** | **635,176** |

The counts above are the exact assignments in the historical image mapping. Use those assignments for benchmark comparisons; do not draw a new 7:1:2 split. The catalogue lists 41 sources, while the image mapping contains 39 named source groups. [The source table](docs/sources.md#source-catalogue) accounts for every catalogue entry and its traceable contribution.

| File | Contents |
|---|---|
| [manifest.csv.gz](metadata/manifest.csv.gz) | All 635,176 sample records: source path, label, prepared path, and split |
| [manifest_examples.csv](metadata/manifest_examples.csv) | Small, directly browsable excerpt with the same columns |
| [classes.csv](metadata/classes.csv) | All 1,167 class IDs/names and per-split counts |
| [source_counts.csv](metadata/source_counts.csv) | Contributions of the 39 mapped source groups |
| [sources.csv](metadata/sources.csv) / [sources.json](metadata/sources.json) | All 41 source links, versions, citations, and recorded data terms |
| [source_label_mapping.json](metadata/source_label_mapping.json) | Historical source-label-to-scientific-name mapping |
| [summary.json](metadata/summary.json) | Counts, preparation protocol, and manifest checksum |
| [datasets.bib](references/datasets.bib) | Importable bibliography for the source datasets |

The manifest is exported from the historical workbook. Per-image hashes, byte sizes, and dimensions were not recorded there and are left empty. [The data dictionary](docs/metadata.md) explains each field and the distinction between fixed membership and image-byte verification.

## Get started

Use Python 3.10 or later. The repository uses Git LFS for existing model weights. Clone the code and metadata without downloading every checkpoint:

```bash
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false clone https://github.com/Kaiqi6/OpenPlant.git
cd OpenPlant
python -m pip install -r requirements.txt
```

Validate the published metadata without downloading or reading images:

```bash
python scripts/validate_dataset.py --manifest metadata/manifest.csv.gz --classes metadata/classes.csv --summary metadata/summary.json --manifest-only
```

### Prepare the images

1. Download the documented source versions from the [source catalogue](docs/sources.md).
2. Arrange the unpacked source directories using [the source-root instructions](docs/reconstruction.md). Keep annotations for the detection sources.
3. Reconstruct the samples listed in the manifest:

```bash
python scripts/build_dataset.py --source-root /path/to/downloads --output-root /path/to/OpenPlant-256 --manifest metadata/manifest.csv.gz
python scripts/validate_dataset.py --output-root /path/to/OpenPlant-256 --manifest metadata/manifest.csv.gz --classes metadata/classes.csv --summary metadata/summary.json
```

The build selects the recorded samples, extracts the specified plant regions where applicable, converts images to RGB, resizes the shorter edge to 256 pixels, and writes PNG files into the fixed `train/`, `val/`, and `test/` folders. It leaves the input files unchanged. Use `--source PlantVillage --limit 10` for a small trial, and `--resume` to verify and reuse previously built outputs.

Some historical paths include renamed files. The reconstruction guide describes directory aliases, explicit file-path mappings, and annotation requirements for resolving those records. Missing inputs are reported rather than replaced with different images.

### Train and evaluate

Install a compatible PyTorch/torchvision pair for your machine, then:

```bash
python -m pip install -r requirements-train.txt
python scripts/train.py --data-root /path/to/OpenPlant-256 --config configs/resnet18.json --manifest metadata/manifest.csv.gz --output runs/resnet18 --device cuda
python scripts/evaluate.py --data-root /path/to/OpenPlant-256 --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights runs/resnet18/best.pt --output runs/resnet18-test --device cuda
```

To retrieve and evaluate an existing OpenPlant checkpoint after installing Git LFS:

```bash
git lfs pull --include="model/resnet18.pth"
python scripts/evaluate.py --data-root /path/to/OpenPlant-256 --config configs/resnet18.json --manifest metadata/manifest.csv.gz --weights model/resnet18.pth --output runs/published-resnet18 --device cuda
```

The [training guide](docs/training.md) lists all 16 configurations, CPU execution, checkpoint resume, metric definitions, and the relationship between the refactored implementation and historical experiments. The paper figures show the published results; this code release does not report a new full benchmark run.

## Dataset diversity

<p align="center">
  <img src="assets/figures/diversity.png" width="49%" alt="Representative plant species across multiple source datasets">
  <img src="assets/figures/diversity_richness.png" width="49%" alt="Comparison of species coverage and image counts">
</p>

*Figure 2 panels: examples across data sources and dataset scale.*

<p align="center">
  <img src="assets/figures/hierarchy.png" width="760" alt="OpenPlant taxonomic hierarchy with example plant images">
</p>

*Figure 3: taxonomic organization of OpenPlant. The paper reports 48 orders, 125 families, and 428 genera.*

## Published benchmark results

![Representative CNN and ViT performance comparison from the paper](assets/figures/radar.png)

*Figure 5b panel: representative CNN/ViT performance across classification metrics.*

![Vision-language model results from the paper](assets/figures/radar_vlm.png)

*Figure 7: comparison of the vision-language models evaluated in the paper.*

See the [complete figure gallery](docs/figures.md) for model evolution, class-level accuracy, PR-AUC, confusion matrices, and example errors. The runnable training pipeline in this release covers CNNs and ViTs; [VLM evaluation scope](docs/training.md#vlm-scope) is documented separately.

## Citation and terms

Please cite OpenPlant and acknowledge the original datasets used in your experiments. The source bibliography includes article, dataset-deposit, and repository citations as appropriate.

```bibtex
@article{liu2026openplant,
  title   = {OpenPlant: A Large-Scale Benchmark Dataset for Agricultural Plant Classification Using CNNs, ViTs, and VLMs},
  author  = {Liu, Kaiqi and Sun, Wei and Wang, Guanping and Feng, Quan and Li, Hui},
  journal = {Plants},
  year    = {2026},
  volume  = {15},
  number  = {5},
  pages   = {727},
  doi     = {10.3390/plants15050727}
}
```

The software is released under the [MIT license](LICENSE). Original images, third-party metadata, model initialization weights, and source annotations retain their respective terms; see [DATA_LICENSE.md](DATA_LICENSE.md) and [the source catalogue](docs/sources.md). This repository hosts the image list and paper figures, while the full underlying image collection is obtained from its original providers.
