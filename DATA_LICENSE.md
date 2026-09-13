# Data, figures, and model terms

## Dataset access

Because of potential copyright and licensing conflicts, we cannot currently
distribute the complete OpenPlant image collection. Some source datasets may
prohibit redistribution of their original or modified images. Obtain images
directly from the [original providers](docs/sources.md) under their respective
terms, then [build OpenPlant locally](docs/reconstruction.md) using the released
manifest and code.

The source catalogue records dataset license declarations. An `unknown` entry
means that permission has not been established. Check the terms for the source
version you obtain, including any image-level licenses. Retain required author
credits, license links, and notices of modifications. A paper's or code repository's
license may differ from the image license.

Two access issues checked on 13 September 2026 need particular attention:

- [CWD30's terms](https://cwd-30.github.io/cwd-30/terms_of_use.html) name
  CC BY-NC-SA 4.0 and also prohibit redistribution of original or modified data.
  Obtain written clarification from the provider before redistributing these
  images, taking account of the license applicable to your copy.
- [PlantNet-300K's metadata](https://github.com/plantnet/PlantNet-300K#dataset-version--meta-data-files)
  includes the author and license for each image. Preserve those records when
  preparing or sharing a permitted subset.

## Code, metadata, and weights

The [MIT license](LICENSE) applies to the software. Third-party images,
annotations, metadata, and model initialization weights retain their original
terms; OpenPlant does not relicense them.

The manifest records OpenPlant's sample selection, label mapping, paths, and fixed
splits. Use it with lawfully obtained source data. The published fine-tuned
checkpoints in `model/` remain subject to applicable model and pretraining terms.

## Figures and artwork

Figures in `assets/figures/` are reproduced from Liu et al., *Plants* 2026, 15(5),
727, DOI [10.3390/plants15050727](https://doi.org/10.3390/plants15050727), using the
authors' supplied assets. The mosaic in `assets/logo/` is author-supplied artwork;
its PNG preview preserves the pixels of the original TIFF. When reusing figures
or artwork, cite OpenPlant and retain applicable credits and permissions for the
source photographs. Their display here does not grant separate redistribution
rights to the underlying photographs.
