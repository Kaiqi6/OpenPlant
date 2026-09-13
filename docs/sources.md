# Dataset sources and composition

OpenPlant contains **635,176 samples in 1,167 classes**. Its catalogue lists
**41 datasets**: 24 disease datasets, 16 crop/weed datasets, and one general plant
dataset. The image manifest traces the selected samples to **39 source groups**.

**We cannot currently distribute the complete OpenPlant image collection because
of potential copyright and licensing conflicts.** Some source datasets may prohibit
redistribution of original or modified images. Obtain the data from the providers
below under their respective terms, then follow the
[reconstruction guide](reconstruction.md) to build OpenPlant locally.
See [data licensing](../DATA_LICENSE.md) for the release policy.

[Image manifest](../metadata/manifest.csv.gz) · [Class list](../metadata/classes.csv) ·
[Sources CSV](../metadata/sources.csv) / [JSON](../metadata/sources.json) ·
[Full bibliography](../references/datasets.bib)

## How the collection is formed

Preparation selects healthy examples from disease datasets, screens poorly visible
plants, standardizes species names, and crops annotated plant regions. The manifest
fixes the retained samples and their train/validation/test assignments.

Counts below refer to output classification images. One photograph can yield
several crops, and classes can occur in several sources. Use the manifest totals
for benchmark comparisons and the documented source versions for reconstruction.

## Source catalogue

`source_id` joins this table to the manifest. CottonWeedDet3 and Carrot-Weed have
`catalogue_only` status: both appear in the paper, but neither has a separate
mapping worksheet or registered adapter. Their contributions remain unresolved
and are shown as **—**.

| # | Source dataset | source_id | Mapped samples | Mapped classes | Access | Citation |
|---:|---|---|---:|---:|---|---|
| 1 | PlantVillage | `PlantVillage` | 18,467 | 12 | [Data](https://data.mendeley.com/datasets/tywbtsjrjv/1) | [2016](#plantvillage) |
| 2 | OLID I | `OLID I` | 786 | 8 | [Data](https://www.kaggle.com/datasets/raiaone/olid-i) | [2023](#olid-i) |
| 3 | PlantDoc | `PlantDoc` | 850 | 10 | [Data](https://github.com/pratikkayal/PlantDoc-Dataset) | [2020](#plantdoc) |
| 4 | Rice Diseases Image Dataset | `RiceDID` | 1,488 | 1 | [Data](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset) | [2019](#ricedid) |
| 5 | Cucumber plant diseases dataset | `CucumberPDD` | 341 | 1 | [Data](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset?select=Cucumber+plant+diseases+dataset) | [2020](#cucumberpdd) |
| 6 | Wheat Leaf Dataset | `WheatLD` | 102 | 1 | [Data](https://data.mendeley.com/datasets/wgd66f8n6h/1) | [2021](#wheatld) |
| 7 | CGIAR Computer Vision for Crop Disease | `CGIAR` | 142 | 1 | [Data](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease) | [2020](#cgiar) |
| 8 | AppleLeaf9 | `AppleLeaf9` | 516 | 1 | [Data](https://github.com/JasonYangCode/AppleLeaf9/tree/main) | [2022](#appleleaf9) |
| 9 | Banana Leaf Disease Images | `BananaLDI` | 155 | 1 | [Data](https://data.mendeley.com/datasets/rjykr62kdh/1) | [2021](#bananaldi) |
| 10 | Apple Tree Leaf Disease Segmentation Dataset | `ATLDSD` | 409 | 1 | [Data](https://www.scidb.cn/en/detail?dataSetId=0e1f57004db842f99668d82183afd578&version=V1) | [2022](#atldsd) |
| 11 | chilli dataset | `chilli` | 2,596 | 1 | [Data](https://data.mendeley.com/datasets/tf9dtfz9m6/2) | [2022](#chilli) |
| 12 | cotton leaf disease dataset | `CottonLDD` | 425 | 1 | [Data](https://www.kaggle.com/datasets/seroshkarim/cotton-leaf-disease-dataset) | [2021](#cottonldd) |
| 13 | Cotton plant disease | `CottonPD` | 800 | 1 | [Data](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease) | [2023](#cottonpd) |
| 14 | Potato Disease Leaf Dataset(PLD) | `PLD` | 1,020 | 1 | [Data](https://www.kaggle.com/datasets/rizwan123456789/potato-disease-leaf-datasetpld) | [2021](#pld) |
| 15 | Cassava Disease Classification | `Cassava` | 316 | 1 | [Data](https://www.kaggle.com/c/cassava-disease/overview) | [2019](#cassava) |
| 16 | Plant Pathology 2020 - FGVC7 | `PP2020` | 516 | 1 | [Data](https://www.kaggle.com/c/plant-pathology-2020-fgvc7/overview) | [2020](#pp2020) |
| 17 | ESCA-dataset | `ESCA` | 882 | 1 | [Data](https://data.mendeley.com/datasets/89cnxc58kj/1) | [2021](#esca) |
| 18 | Sugarcane Leaf Disease Dataset | `SugarcaneLDD` | 522 | 1 | [Data](https://data.mendeley.com/datasets/9424skmnrk/1) | [2022](#sugarcaneldd) |
| 19 | Corn Leaf Disease | `CornLD` | 1,000 | 1 | [Data](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease) | [2023](#cornld) |
| 20 | Mango Leaf Disease Dataset | `MangoLeafBD` | 500 | 1 | [Data](https://data.mendeley.com/datasets/hxsnvwty3r/1) | [2023](#mangoleafbd) |
| 21 | Soybean images dataset | `Soybean Leaves` | 896 | 1 | [Data](https://data.mendeley.com/datasets/bycbh73438/1) | [2022](#soybean-leaves) |
| 22 | Sugarcane Disease Dataset | `SugarcaneDD` | 100 | 1 | [Data](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset) | [2022](#sugarcanedd) |
| 23 | Coffee plant disease | `Coffee plant disease` | 435 | 1 | [Data](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease) | [2021](#coffee-plant-disease) |
| 24 | Database of Leaf Images/Fruit Leaf | `Fruit Leaf` | 2,277 | 11 | [Data](https://data.mendeley.com/datasets/hb74ynkjcn/4) | [2019](#fruit-leaf) |
| 25 | Weed25 | `Weed25` | 17,436 | 25 | [Data](https://pan.baidu.com/s/1rnUoDm7IxxmX1n1LmtXNXw) | [2022](#weed25) |
| 26 | CottonWeedDet12 | `CottonWeedDet12` | 8,826 | 10 | [Data](https://weed-ai.sydney.edu.au/datasets/2c14915b-0827-4b65-9908-d2a6df0d48f3) | [2023](#cottonweeddet12) |
| 27 | DeepWeeds | `DeepWeeds` | 8,403 | 8 | [Data](https://www.kaggle.com/datasets/imsparsh/deepweeds) | [2019](#deepweeds) |
| 28 | CottonWeedID15 | `CWID15` | 1,785 | 8 | [Data](https://www.kaggle.com/datasets/yuzhenlu/cottonweedid15) | [2022](#cwid15) |
| 29 | SugarBeet2016 | `WeedNet-R` | 6,524 | 1 | [Data](https://github.com/GOOJJJ/WeedNet-R/) | [2023](#weednet-r) |
| 30 | CWD30 | `CWD30` | 122,427 | 30 | [Data](https://github.com/Mr-TalhaIlyas/CWD30) | [2025](#cwd30) |
| 31 | Plant Seedlings Classification | `PlantSeedlings` | 5,539 | 12 | [Data](https://vision.eng.au.dk/plant-seedlings-dataset/) | [2017](#plantseedlings) |
| 32 | PlantNet-300K | `plantnet_300K` | 306,146 | 1021 | [Data](https://zenodo.org/records/5645731) | [2021](#plantnet-300k) |
| 33 | early-crop-weed | `Early_crop_weed` | 508 | 4 | [Data](https://github.com/AUAgroup/early-crop-weed) | [2024](#early-crop-weed) |
| 34 | Open Plant Phenotyping Database | `OPPD` | 97,962 | 47 | [Data](https://vision.eng.au.dk/open-plant-phenotyping-database/) | [2020](#oppd) |
| 35 | CottonWeedDet3 | `CottonWeedDet3` | — | — | [Data](https://www.kaggle.com/datasets/yuzhenlu/cottonweeddet3) | [2023](#cottonweeddet3) |
| 36 | weed-datasets | `weed-datasets` | 6,699 | 7 | [Data](https://github.com/zhangchuanyin/weed-datasets) | [2023](#weed-datasets) |
| 37 | Carrot-Weed | `Carrot-Weed` | — | — | [Data](https://github.com/lameski/rgbweeddetection) | [2017](#carrot-weed) |
| 38 | Vegetable Crops Dataset for Proximal Sensing (VCD) | `VCD` | 4,009 | 3 | [Data](https://data.mendeley.com/datasets/d7kbzjr83k/1) | [2022](#vcd) |
| 39 | SorghumWeedDataset_Classification | `SorghumWeed` | 1,404 | 1 | [Data](https://data.mendeley.com/datasets/4gkcyxjyss/1) | [2024](#sorghumweed) |
| 40 | ImageWeeds | `ImageWeeds` | 4,509 | 4 | [Data](https://data.mendeley.com/datasets/8kjcztbjz2/2) | [2023](#imageweeds) |
| 41 | TobSet | `TobSet` | 7,458 | 1 | [Data](https://github.com/mshahabalam/TobSet) | [2022](#tobset) |

## References, versions and dataset terms

References include papers, preprints, data deposits and repositories. Full author
lists are in the bibliography; verification records are in the JSON.

License labels below reproduce the source metadata reviewed on 12 September 2026.
`unknown` means no data license is recorded there. Check the image terms applicable
to the source version you obtain and retain attribution; a paper or code license
alone does not establish image-reuse rights.
The CWD30 and PlantNet-300K entries include additional terms to check before reuse.

<a id="plantvillage"></a>

### PlantVillage

[Data](https://data.mendeley.com/datasets/tywbtsjrjv/1) · License: `CC0-1.0` · [Dataset DOI](https://doi.org/10.17632/tywbtsjrjv.1)

Hughes and Salathe (2016). [An Open Access Repository of Images on Plant Health to Enable the Development of Mobile Disease Diagnostics](https://doi.org/10.48550/arXiv.1511.08060). arXiv. `hughesOpenAccessRepository2016`.

ARUN PANDIAN J and GEETHARAMANI GOPAL (2019). [Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network](https://data.mendeley.com/datasets/tywbtsjrjv/1). Mendeley Data. `pandianPlantVillageDeposit2019`.

Use the recorded augmented deposit (61,486 images), read by the original adapter as `Plant_leave_diseases_dataset_with_augmentation`. The catalogue's 54,309 refers to PlantVillage generally. CC0 is the deposit's declaration; upstream image rights still need checking.

<a id="olid-i"></a>

### OLID I

[Data](https://www.kaggle.com/datasets/raiaone/olid-i) · License: `unknown`

Orka et al. (2023). [OLID I: An Open Leaf Image Dataset for Plant Stress Recognition](https://doi.org/10.3389/fpls.2023.1251888). Front. Plant Sci. `orkaOLIDOpenLeaf2023`.

<a id="plantdoc"></a>

### PlantDoc

[Data](https://github.com/pratikkayal/PlantDoc-Dataset) · License: `unknown`

Singh et al. (2020). [PlantDoc: A Dataset for Visual Plant Disease Detection](https://doi.org/10.1145/3371158.3371196). Proceedings of the 7th ACM IKDD CoDS and 25th COMAD. `singhPlantDocDatasetVisual2020`.

<a id="ricedid"></a>

### Rice Diseases Image Dataset

[Data](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset) · License: `unknown`

Huy Minh Do (2019). [Rice Diseases Image Dataset](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset). `huyminhdoRice2019`.

<a id="cucumberpdd"></a>

### Cucumber plant diseases dataset

[Data](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset?select=Cucumber+plant+diseases+dataset) · License: `unknown`

Karim Negm (2020). [Cucumber Plant Diseases Dataset](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset). `karimnegmCucumber2020`.

<a id="wheatld"></a>

### Wheat Leaf Dataset

[Data](https://data.mendeley.com/datasets/wgd66f8n6h/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/wgd66f8n6h.1)

Getachew (2021). [Wheat Leaf Dataset](https://data.mendeley.com/datasets/wgd66f8n6h/1). Mendeley Data. `getachewWheat2021`.

<a id="cgiar"></a>

### CGIAR Computer Vision for Crop Disease

[Data](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease) · License: `unknown`

Shadab Hussain (2020). [CGIAR Computer Vision for Crop Disease](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease). `shadabhussainCGIAR2020`.

The spreadsheet linked the AppleLeaf9 paper here. This entry uses the CGIAR data citation from the manuscript.

<a id="appleleaf9"></a>

### AppleLeaf9

[Data](https://github.com/JasonYangCode/AppleLeaf9/tree/main) · License: `unknown`

Yang et al. (2022). [Efficient Identification of Apple Leaf Diseases in the Wild Using Convolutional Neural Networks](https://doi.org/10.3390/agronomy12112784). Agronomy. `yangEfficientIdentificationApple2022`.

<a id="bananaldi"></a>

### Banana Leaf Disease Images

[Data](https://data.mendeley.com/datasets/rjykr62kdh/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/rjykr62kdh.1)

Hailu (2021). [Banana Leaf Disease Images](https://data.mendeley.com/datasets/rjykr62kdh/1). Mendeley Data. `hailuBanana2021`.

<a id="atldsd"></a>

### Apple Tree Leaf Disease Segmentation Dataset

[Data](https://www.scidb.cn/en/detail?dataSetId=0e1f57004db842f99668d82183afd578&version=V1) · License: `unknown`

Feng and Chao (2022). [Apple Tree Leaf Disease Segmentation Dataset](https://doi.org/10.11922/sciencedb.01627). `fengApple2022`.

<a id="chilli"></a>

### chilli dataset

[Data](https://data.mendeley.com/datasets/tf9dtfz9m6/2) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/tf9dtfz9m6.2)

Naik et al. (2022). [Detection and Classification of Chilli Leaf Disease Using a Squeeze-and-Excitation-Based CNN Model](https://doi.org/10.1016/j.ecoinf.2022.101663). Ecol. Inf. `naikDetection2022`.

Aishwarya M P and Padmanabha Reddy (2024). [chilli dataset](https://data.mendeley.com/datasets/tf9dtfz9m6/2). Mendeley Data. `aishwaryaChilliDeposit2024`.

The download is Mendeley V2 (2024), deposited by Aishwarya M P and Padmanabha Reddy. The manuscript cites Naik et al. (2022); the deposit does not establish that connection. Both references are retained.

<a id="cottonldd"></a>

### cotton leaf disease dataset

[Data](https://www.kaggle.com/datasets/seroshkarim/cotton-leaf-disease-dataset) · License: `unknown`

Noon et al. (2021). [Computationally Light Deep Learning Framework to Recognize Cotton Leaf Diseases](https://doi.org/10.3233/JIFS-210516). J. Intell. Fuzzy Syst. `noonComputationally2021`.

<a id="cottonpd"></a>

### Cotton plant disease

[Data](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease) · License: `unknown`

Dhamodharan R (2023). [Cotton Plant Disease](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease). `dhamodharanrCotton2023`.

<a id="pld"></a>

### Potato Disease Leaf Dataset(PLD)

[Data](https://www.kaggle.com/datasets/rizwan123456789/potato-disease-leaf-datasetpld) · License: `unknown`

Rashid et al. (2021). [Multi-Level Deep Learning Model for Potato Leaf Disease Recognition](https://doi.org/10.3390/electronics10172064). Electronics. `rashidMultilevelDeepLearning2021a`.

Upstream totals differ: 4,072 in the spreadsheet and 4,062 in the paper. The manifest contains 1,020 selected images.

<a id="cassava"></a>

### Cassava Disease Classification

[Data](https://www.kaggle.com/c/cassava-disease/overview) · License: `unknown`

Mwebaze et al. (2019). [iCassava 2019 Fine-Grained Visual Categorization Challenge](https://doi.org/10.48550/arXiv.1908.02900). arXiv. `mwebazeICassava2019Finegrained2019`.

The link and paper describe the 2019 iCassava challenge; the catalogue lists 21,400 images without an archive version. Use the manifest's filenames for the 316 selected images.

<a id="pp2020"></a>

### Plant Pathology 2020 - FGVC7

[Data](https://www.kaggle.com/c/plant-pathology-2020-fgvc7/overview) · License: `unknown`

Thapa et al. (2020). [The Plant Pathology Challenge 2020 Data Set to Classify Foliar Disease of Apples](https://doi.org/10.1002/aps3.11390). Appl. Plant Sci. `thapaPlant2020`.

<a id="esca"></a>

### ESCA-dataset

[Data](https://data.mendeley.com/datasets/89cnxc58kj/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/89cnxc58kj.1)

Alessandrini et al. (2021). [A Grapevine Leaves Dataset for Early Detection and Classification of Esca Disease in Vineyards through Machine Learning](https://doi.org/10.1016/j.dib.2021.106809). Data Brief. `alessandriniGrapevine2021`.

<a id="sugarcaneldd"></a>

### Sugarcane Leaf Disease Dataset

[Data](https://data.mendeley.com/datasets/9424skmnrk/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/9424skmnrk.1)

Daphal and Koli (2022). [Sugarcane Leaf Disease Dataset](https://data.mendeley.com/datasets/9424skmnrk/1). Mendeley Data. `daphalSugarcane2022`.

<a id="cornld"></a>

### Corn Leaf Disease

[Data](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease) · License: `unknown`

Sandi Indika Saputra (2023). [Corn Leaf Disease](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease). `sandiindikasaputraCorn2023`.

<a id="mangoleafbd"></a>

### Mango Leaf Disease Dataset

[Data](https://data.mendeley.com/datasets/hxsnvwty3r/1) · License: `CC-BY-NC-3.0` · [Dataset DOI](https://doi.org/10.17632/hxsnvwty3r.1)

Ahmed et al. (2023). [MangoLeafBD: A Comprehensive Image Dataset to Classify Diseased and Healthy Mango Leaves](https://doi.org/10.1016/j.dib.2023.108941). Data Brief. `ahmedMangoLeafBD2023`.

<a id="soybean-leaves"></a>

### Soybean images dataset

[Data](https://data.mendeley.com/datasets/bycbh73438/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/bycbh73438.1)

Mignoni et al. (2022). [Soybean Images Dataset for Caterpillar and Diabrotica Speciosa Pest Detection and Classification](https://doi.org/10.1016/j.dib.2021.107756). Data Brief. `mignoniSoybean2022`.

<a id="sugarcanedd"></a>

### Sugarcane Disease Dataset

[Data](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset) · License: `unknown`

Prabhakaran Soundar (2022). [Sugarcane Disease Dataset](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset). `prabhakaransoundarSugarcane2022`.

<a id="coffee-plant-disease"></a>

### Coffee plant disease

[Data](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease) · License: `unknown`

Coffee Disease (2021). [Coffee Plant Disease](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease). `coffeediseaseCoffee2021`.

<a id="fruit-leaf"></a>

### Database of Leaf Images/Fruit Leaf

[Data](https://data.mendeley.com/datasets/hb74ynkjcn/4) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/hb74ynkjcn.4)

Chouhan et al. (2019). [A Data Repository of Leaf Images: Practice towards Plant Conservation with Plant Pathology](https://doi.org/10.1109/ISCON47742.2019.9036158). 2019 4th International Conference on Information Systems and Computer Networks (ISCON). `chouhanDataRepositoryLeaf2019`.

<a id="weed25"></a>

### Weed25

[Data](https://pan.baidu.com/s/1rnUoDm7IxxmX1n1LmtXNXw) · License: `unknown` · [Project / access page](https://doi.org/10.3389/fpls.2022.1053329)

Wang et al. (2022). [Weed25: A Deep Learning Dataset for Weed Identification](https://doi.org/10.3389/fpls.2022.1053329). Front. Plant Sci. `wangWeed25DeepLearning2022`.

Baidu access code: **rn5h**, as supplied in the paper. The recorded access page is the paper DOI.

<a id="cottonweeddet12"></a>

### CottonWeedDet12

[Data](https://weed-ai.sydney.edu.au/datasets/2c14915b-0827-4b65-9908-d2a6df0d48f3) · License: `unknown`

Dang et al. (2023). [YOLOWeeds: A Novel Benchmark of YOLO Object Detectors for Multi-Class Weed Detection in Cotton Production Systems](https://doi.org/10.1016/j.compag.2023.107655). Comput. Electron. Agric. `dangYOLOWeeds2023`.

<a id="deepweeds"></a>

### DeepWeeds

[Data](https://www.kaggle.com/datasets/imsparsh/deepweeds) · License: `unknown`

Olsen et al. (2019). [DeepWeeds: A Multiclass Weed Species Image Dataset for Deep Learning](https://doi.org/10.1038/s41598-018-38343-3). Sci. Rep. `olsenDeepWeeds2019`.

<a id="cwid15"></a>

### CottonWeedID15

[Data](https://www.kaggle.com/datasets/yuzhenlu/cottonweedid15) · License: `unknown`

Chen et al. (2022). [Performance Evaluation of Deep Transfer Learning on Multi-Class Identification of Common Weed Species in Cotton Production Systems](https://doi.org/10.1016/j.compag.2022.107091). Comput. Electron. Agric. `chenPerformance2022`.

<a id="weednet-r"></a>

### SugarBeet2016

[Data](https://github.com/GOOJJJ/WeedNet-R/) · License: `unknown`

Guo et al. (2023). [WeedNet-R: A Sugar Beet Field Weed Detection Algorithm Based on Enhanced RetinaNet and Context Semantic Fusion](https://doi.org/10.3389/fpls.2023.1226329). Front. Plant Sci. `guoWeedNetRSugarBeet2023`.

SugarBeet2016 uses the WeedNet-R adapter and worksheet. The repository credits Sugar Beets 2016 as its source; OpenPlant counts the extracted plant crops.

<a id="cwd30"></a>

### CWD30

[Data](https://github.com/Mr-TalhaIlyas/CWD30) · License: `unknown` · [Project / access page](https://github.com/mr-talhailyas/cwd30)

Ilyas et al. (2025). [CWD30: A New Benchmark Dataset for Crop Weed Recognition in Precision Agriculture](https://doi.org/10.1016/j.compag.2024.109737). Comput. Electron. Agric. `ilyasCWD302025`.

The [official Terms of Use](https://cwd-30.github.io/cwd-30/terms_of_use.html) declare CC BY-NC-SA 4.0 and separately prohibit redistribution of original or modified data. See [data licensing](../DATA_LICENSE.md) for this conflict.

<a id="plantseedlings"></a>

### Plant Seedlings Classification

[Data](https://vision.eng.au.dk/plant-seedlings-dataset/) · License: `CC-BY-SA-4.0`

Giselsson et al. (2017). [A Public Image Database for Benchmark of Plant Seedling Classification Algorithms](https://doi.org/10.48550/arXiv.1711.05458). arXiv. `giselssonPublicImageDatabase2017`.

Use the official page's **NonsegmentedV2** download, as specified by the adapter.

<a id="plantnet-300k"></a>

### PlantNet-300K

[Data](https://zenodo.org/records/5645731) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.5281/zenodo.5645731) · [Project / access page](https://github.com/plantnet/PlantNet-300K) · [License declaration](https://api.datacite.org/dois/10.5281/zenodo.5645731)

Garcin et al. (2021). [Pl@ntNet-300K Image Dataset](https://doi.org/10.5281/ZENODO.5645731). Zenodo. `garcinPlntNet300KImageDataset2021`.

Garcin et al. (2021). [Pl@ntNet-300K: a plant image dataset with high label ambiguity and a long-tailed distribution](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/7e7757b1e12abcb736ab9a754ffb617a-Paper-round2.pdf). NeurIPS Datasets and Benchmarks. `garcinPlantNetPaper2021`.

Zenodo V1.1 declares CC BY 4.0 at deposit level. The official repository provides per-image author and license metadata: retain it and check each image's terms. Its 1,081 upstream labels map to 1,021 distinct class names in OpenPlant.

<a id="early-crop-weed"></a>

### early-crop-weed

[Data](https://github.com/AUAgroup/early-crop-weed) · License: `unknown`

AUAgroup (2024). [AUAgroup/Early-Crop-Weed](https://github.com/AUAgroup/early-crop-weed). `auagroupAUAgroup2024`.

<a id="oppd"></a>

### Open Plant Phenotyping Database

[Data](https://vision.eng.au.dk/open-plant-phenotyping-database/) · License: `CC-BY-NC-SA-4.0`

Leminen Madsen et al. (2020). [Open Plant Phenotype Database of Common Weeds in Denmark](https://doi.org/10.3390/rs12081246). Remote Sens. `leminenmadsenOpen2020`.

The upstream total of 315,038 counts plant objects in 7,590 RGB photographs. OpenPlant selects individual-plant images from `images_plants`.

<a id="cottonweeddet3"></a>

### CottonWeedDet3

[Data](https://www.kaggle.com/datasets/yuzhenlu/cottonweeddet3) · License: `unknown`

Rahman et al. (2023). [Performance Evaluation of Deep Learning Object Detectors for Weed Detection for Cotton](https://doi.org/10.1016/j.atech.2022.100126). Smart Agric. Technol. `rahmanPerformance2023`.

<a id="weed-datasets"></a>

### weed-datasets

[Data](https://github.com/zhangchuanyin/weed-datasets) · License: `unknown`

zhangchuanyin (2023). [Zhangchuanyin/Weed-Datasets](https://github.com/zhangchuanyin/weed-datasets). `zhangchuanyinZhangchuanyin2023`.

<a id="carrot-weed"></a>

### Carrot-Weed

[Data](https://github.com/lameski/rgbweeddetection) · License: `unknown`

Lameski et al. (2017). [Weed Detection Dataset with RGB Images Taken under Variable Light Conditions](https://doi.org/10.1007/978-3-319-67597-8_11). ICT Innovations 2017. `lameskiWeedDetectionDataset2017`.

<a id="vcd"></a>

### Vegetable Crops Dataset for Proximal Sensing (VCD)

[Data](https://data.mendeley.com/datasets/d7kbzjr83k/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/d7kbzjr83k.1)

Lac et al. (2022). [An Annotated Image Dataset of Vegetable Crops at an Early Stage of Growth for Proximal Sensing Applications](https://doi.org/10.1016/j.dib.2022.108035). Data Brief. `lacAnnotated2022`.

<a id="sorghumweed"></a>

### SorghumWeedDataset_Classification

[Data](https://data.mendeley.com/datasets/4gkcyxjyss/1) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/4gkcyxjyss.1)

Justina and Thenmozhi (2024). [SorghumWeedDataset_Classification and SorghumWeedDataset_Segmentation Datasets for Classification, Detection, and Segmentation in Deep Learning](https://doi.org/10.1016/j.dib.2023.109935). Data Brief. `justinaSorghumWeedDataset_Classification2024`.

The manifest includes the 1,404 sorghum images. Generic grass and broad-leaf weed labels are omitted.

<a id="imageweeds"></a>

### ImageWeeds

[Data](https://data.mendeley.com/datasets/8kjcztbjz2/2) · License: `CC-BY-4.0` · [Dataset DOI](https://doi.org/10.17632/8kjcztbjz2.2) · [License declaration](https://api.datacite.org/dois/10.17632/8kjcztbjz2.2)

Rai et al. (2023). [Multi-Format Open-Source Weed Image Dataset for Real-Time Weed Identification in Precision Agriculture](https://doi.org/10.1016/j.dib.2023.109691). Data Brief. `raiMultiformat2023`.

DataCite confirms the V2 deposit and CC BY 4.0 declaration. If the Mendeley page is unavailable, consult the linked paper for access information.

<a id="tobset"></a>

### TobSet

[Data](https://github.com/mshahabalam/TobSet) · License: `unknown`

Alam et al. (2022). [TobSet: A New Tobacco Crop and Weeds Image Dataset and Its Utilization for Vision-Based Spraying by Agricultural Robots](https://doi.org/10.3390/app12031308). Appl. Sci. `alamTobSet2022`.

## Provenance

Counts come from the 39 source worksheets in `image_mapping_test_0220.xlsx`.
Sheet4 of `datasets(已自动还原).xlsx` supplies the catalogue; `openplant.bib`
supplies the manuscript references, supplemented by primary-source records.
The JSON includes their SHA-256 hashes. `catalogue_image_count` stores the
historical upstream totals; `mapped_samples` counts OpenPlant's selected images.

Regenerate the source files from those inputs:

```bash
python tools/export_sources.py --catalogue /path/to/catalogue.xlsx \
  --mapping /path/to/image_mapping_test_0220.xlsx \
  --bibliography /path/to/openplant.bib --output . --verify-dois
```

`--verify-dois` checks article DOIs through Crossref. Data-license declarations
have separate evidence links in the source records.
