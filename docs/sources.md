# Dataset sources and composition

OpenPlant's released image list contains **635,176 samples across 1,167 classes**.
The historical source catalogue contains **41 entries**: 24 disease datasets,
16 crop/weed datasets, and one general plant dataset. The recovered image mapping
assigns samples to **39 named source worksheets**. This page preserves all 41
catalogue entries and reports the contribution that can be traced to each worksheet.

Use [manifest.csv.gz](../metadata/manifest.csv.gz) for exact sample membership and
fixed train/validation/test assignments, and [classes.csv](../metadata/classes.csv)
for the class vocabulary. Machine-readable source records are available as
[CSV](../metadata/sources.csv) and [JSON](../metadata/sources.json); all references
can be imported from [datasets.bib](../references/datasets.bib).

## How the collection is formed

The paper describes selection of healthy examples from disease datasets, screening
of poorly visible plants, taxonomic name standardization, and extraction of plant
regions from object annotations. The released manifest records the retained
samples after these operations. Its counts are output classification images;
multiple crops may come from one upstream photograph. Upstream catalogue totals
therefore cannot be subtracted from these counts to infer the number of rejected
photographs. Source class counts also overlap and must not be summed to obtain
OpenPlant's 1,167 classes.

Download the sources from the links below and use the reconstruction instructions
in the repository. Preserve the recorded source version where available and the
manifest's fixed splits when comparing with the paper. A new random split defines
a different experiment.

## Source catalogue

`source_id` is the stable join key used by the image manifest. **—** means that no
separate contribution is recoverable from the image mapping, rather than a verified
zero-image selection. CottonWeedDet3 and Carrot-Weed are listed in the original
catalogue and paper, but neither has its own worksheet or registered adapter in the
recovered build. They remain in this catalogue with `catalogue_only` status;
the available records do not establish whether they were excluded or merged.

| # | Source dataset | source_id | Mapped samples | Mapped classes | Access | Citation |
|---:|---|---|---:|---:|---|---|
| 1 | PlantVillage | `PlantVillage` | 18,467 | 12 | [Data / homepage](https://data.mendeley.com/datasets/tywbtsjrjv/1) | [2016](#plantvillage) |
| 2 | OLID I | `OLID I` | 786 | 8 | [Data / homepage](https://www.kaggle.com/datasets/raiaone/olid-i) | [2023](#olid-i) |
| 3 | PlantDoc | `PlantDoc` | 850 | 10 | [Data / homepage](https://github.com/pratikkayal/PlantDoc-Dataset) | [2020](#plantdoc) |
| 4 | Rice Diseases Image Dataset | `RiceDID` | 1,488 | 1 | [Data / homepage](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset) | [2019](#ricedid) |
| 5 | Cucumber plant diseases dataset | `CucumberPDD` | 341 | 1 | [Data / homepage](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset?select=Cucumber+plant+diseases+dataset) | [2020](#cucumberpdd) |
| 6 | Wheat Leaf Dataset | `WheatLD` | 102 | 1 | [Data / homepage](https://data.mendeley.com/datasets/wgd66f8n6h/1) | [2021](#wheatld) |
| 7 | CGIAR Computer Vision for Crop Disease | `CGIAR` | 142 | 1 | [Data / homepage](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease) | [2020](#cgiar) |
| 8 | AppleLeaf9 | `AppleLeaf9` | 516 | 1 | [Data / homepage](https://github.com/JasonYangCode/AppleLeaf9/tree/main) | [2022](#appleleaf9) |
| 9 | Banana Leaf Disease Images | `BananaLDI` | 155 | 1 | [Data / homepage](https://data.mendeley.com/datasets/rjykr62kdh/1) | [2021](#bananaldi) |
| 10 | Apple Tree Leaf Disease Segmentation Dataset | `ATLDSD` | 409 | 1 | [Data / homepage](https://www.scidb.cn/en/detail?dataSetId=0e1f57004db842f99668d82183afd578&version=V1) | [2022](#atldsd) |
| 11 | chilli dataset | `chilli` | 2,596 | 1 | [Data / homepage](https://data.mendeley.com/datasets/tf9dtfz9m6/2) | [2022](#chilli) |
| 12 | cotton leaf disease dataset | `CottonLDD` | 425 | 1 | [Data / homepage](https://www.kaggle.com/datasets/seroshkarim/cotton-leaf-disease-dataset) | [2021](#cottonldd) |
| 13 | Cotton plant disease | `CottonPD` | 800 | 1 | [Data / homepage](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease) | [2023](#cottonpd) |
| 14 | Potato Disease Leaf Dataset(PLD) | `PLD` | 1,020 | 1 | [Data / homepage](https://www.kaggle.com/datasets/rizwan123456789/potato-disease-leaf-datasetpld) | [2021](#pld) |
| 15 | Cassava Disease Classification | `Cassava` | 316 | 1 | [Data / homepage](https://www.kaggle.com/c/cassava-disease/overview) | [2019](#cassava) |
| 16 | Plant Pathology 2020 - FGVC7 | `PP2020` | 516 | 1 | [Data / homepage](https://www.kaggle.com/c/plant-pathology-2020-fgvc7/overview) | [2020](#pp2020) |
| 17 | ESCA-dataset | `ESCA` | 882 | 1 | [Data / homepage](https://data.mendeley.com/datasets/89cnxc58kj/1) | [2021](#esca) |
| 18 | Sugarcane Leaf Disease Dataset | `SugarcaneLDD` | 522 | 1 | [Data / homepage](https://data.mendeley.com/datasets/9424skmnrk/1) | [2022](#sugarcaneldd) |
| 19 | Corn Leaf Disease | `CornLD` | 1,000 | 1 | [Data / homepage](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease) | [2023](#cornld) |
| 20 | Mango Leaf Disease Dataset | `MangoLeafBD` | 500 | 1 | [Data / homepage](https://data.mendeley.com/datasets/hxsnvwty3r/1) | [2023](#mangoleafbd) |
| 21 | Soybean images dataset | `Soybean Leaves` | 896 | 1 | [Data / homepage](https://data.mendeley.com/datasets/bycbh73438/1) | [2022](#soybean-leaves) |
| 22 | Sugarcane Disease Dataset | `SugarcaneDD` | 100 | 1 | [Data / homepage](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset) | [2022](#sugarcanedd) |
| 23 | Coffee plant disease | `Coffee plant disease` | 435 | 1 | [Data / homepage](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease) | [2021](#coffee-plant-disease) |
| 24 | Database of Leaf Images/Fruit Leaf | `Fruit Leaf` | 2,277 | 11 | [Data / homepage](https://data.mendeley.com/datasets/hb74ynkjcn/4) | [2019](#fruit-leaf) |
| 25 | Weed25 | `Weed25` | 17,436 | 25 | [Data / homepage](https://pan.baidu.com/s/1rnUoDm7IxxmX1n1LmtXNXw) | [2022](#weed25) |
| 26 | CottonWeedDet12 | `CottonWeedDet12` | 8,826 | 10 | [Data / homepage](https://weed-ai.sydney.edu.au/datasets/2c14915b-0827-4b65-9908-d2a6df0d48f3) | [2023](#cottonweeddet12) |
| 27 | DeepWeeds | `DeepWeeds` | 8,403 | 8 | [Data / homepage](https://www.kaggle.com/datasets/imsparsh/deepweeds) | [2019](#deepweeds) |
| 28 | CottonWeedID15 | `CWID15` | 1,785 | 8 | [Data / homepage](https://www.kaggle.com/datasets/yuzhenlu/cottonweedid15) | [2022](#cwid15) |
| 29 | SugarBeet2016 | `WeedNet-R` | 6,524 | 1 | [Data / homepage](https://github.com/GOOJJJ/WeedNet-R/) | [2023](#weednet-r) |
| 30 | CWD30 | `CWD30` | 122,427 | 30 | [Data / homepage](https://github.com/Mr-TalhaIlyas/CWD30) | [2025](#cwd30) |
| 31 | Plant Seedlings Classification | `PlantSeedlings` | 5,539 | 12 | [Data / homepage](https://vision.eng.au.dk/plant-seedlings-dataset/) | [2017](#plantseedlings) |
| 32 | PlantNet-300K | `plantnet_300K` | 306,146 | 1021 | [Data / homepage](https://zenodo.org/records/5645731) | [2021](#plantnet-300k) |
| 33 | early-crop-weed | `Early_crop_weed` | 508 | 4 | [Data / homepage](https://github.com/AUAgroup/early-crop-weed) | [2024](#early-crop-weed) |
| 34 | Open Plant Phenotyping Database | `OPPD` | 97,962 | 47 | [Data / homepage](https://vision.eng.au.dk/open-plant-phenotyping-database/) | [2020](#oppd) |
| 35 | CottonWeedDet3 | `CottonWeedDet3` | — | — | [Data / homepage](https://www.kaggle.com/datasets/yuzhenlu/cottonweeddet3) | [2023](#cottonweeddet3) |
| 36 | weed-datasets | `weed-datasets` | 6,699 | 7 | [Data / homepage](https://github.com/zhangchuanyin/weed-datasets) | [2023](#weed-datasets) |
| 37 | Carrot-Weed | `Carrot-Weed` | — | — | [Data / homepage](https://github.com/lameski/rgbweeddetection) | [2017](#carrot-weed) |
| 38 | Vegetable Crops Dataset for Proximal Sensing (VCD) | `VCD` | 4,009 | 3 | [Data / homepage](https://data.mendeley.com/datasets/d7kbzjr83k/1) | [2022](#vcd) |
| 39 | SorghumWeedDataset_Classification | `SorghumWeed` | 1,404 | 1 | [Data / homepage](https://data.mendeley.com/datasets/4gkcyxjyss/1) | [2024](#sorghumweed) |
| 40 | ImageWeeds | `ImageWeeds` | 4,509 | 4 | [Data / homepage](https://data.mendeley.com/datasets/8kjcztbjz2/2) | [2023](#imageweeds) |
| 41 | TobSet | `TobSet` | 7,458 | 1 | [Data / homepage](https://github.com/mshahabalam/TobSet) | [2022](#tobset) |

## References, versions and dataset terms

The citations below follow the manuscript bibliography. A citation may be an
article, preprint, dataset deposit, or repository; a data-page citation does not
imply a separate research paper. The JSON records expose citation-verification
status and evidence URLs. Dataset license declarations come from the linked data
pages or their DataCite records reviewed on 12 September 2026. `unknown` means that a dataset
license was not established in this review. Consult each source's current terms
and preserve its required attribution. Article and code licenses are not used as
substitutes for image licenses.

<a id="plantvillage"></a>

### PlantVillage

**Source ID:** `PlantVillage` · **Dataset license:** `CC0-1.0`

[Data / homepage](https://data.mendeley.com/datasets/tywbtsjrjv/1) · [Dataset DOI](https://doi.org/10.17632/tywbtsjrjv.1)

Hughes, David P. and Salathe, Marcel (2016). [An Open Access Repository of Images on Plant Health to Enable the Development of Mobile Disease Diagnostics](https://doi.org/10.48550/arXiv.1511.08060). arXiv. BibTeX: `hughesOpenAccessRepository2016`.

ARUN PANDIAN J and GEETHARAMANI GOPAL (2019). [Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network](https://data.mendeley.com/datasets/tywbtsjrjv/1). Mendeley Data. BibTeX: `pandianPlantVillageDeposit2019`.

The original adapter uses Plant_leave_diseases_dataset_with_augmentation. The recorded Mendeley deposit reports 61,486 augmented images; the catalogue's 54,309 describes PlantVillage generally. Reconstruct from the recorded deposit and manifest, not an interchangeable PlantVillage mirror. The displayed CC0 label is the deposit's declaration, not an independent clearance of upstream image rights.

<a id="olid-i"></a>

### OLID I

**Source ID:** `OLID I` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/raiaone/olid-i)

Orka, Nabil Anan and Uddin, M. Nazim and Toushique, Fardeen Md. and Hossain, M. Shahadath (2023). [OLID I: An Open Leaf Image Dataset for Plant Stress Recognition](https://doi.org/10.3389/fpls.2023.1251888). Front. Plant Sci.. BibTeX: `orkaOLIDOpenLeaf2023`.

<a id="plantdoc"></a>

### PlantDoc

**Source ID:** `PlantDoc` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/pratikkayal/PlantDoc-Dataset)

Singh, Davinder and Jain, Naman and Jain, Pranjali and Kayal, Pratik and Kumawat, Sudhakar and Batra, Nipun (2020). [PlantDoc: A Dataset for Visual Plant Disease Detection](https://doi.org/10.1145/3371158.3371196). Proceedings of the 7th ACM IKDD CoDS and 25th COMAD. BibTeX: `singhPlantDocDatasetVisual2020`.

<a id="ricedid"></a>

### Rice Diseases Image Dataset

**Source ID:** `RiceDID` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset)

Huy Minh Do (2019). [Rice Diseases Image Dataset](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset). BibTeX: `huyminhdoRice2019`.

<a id="cucumberpdd"></a>

### Cucumber plant diseases dataset

**Source ID:** `CucumberPDD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset?select=Cucumber+plant+diseases+dataset)

Karim Negm (2020). [Cucumber Plant Diseases Dataset](https://www.kaggle.com/datasets/kareem3egm/cucumber-plant-diseases-dataset). BibTeX: `karimnegmCucumber2020`.

<a id="wheatld"></a>

### Wheat Leaf Dataset

**Source ID:** `WheatLD` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/wgd66f8n6h/1) · [Dataset DOI](https://doi.org/10.17632/wgd66f8n6h.1)

Getachew, Hawi (2021). [Wheat Leaf Dataset](https://data.mendeley.com/datasets/wgd66f8n6h/1). Mendeley Data. BibTeX: `getachewWheat2021`.

<a id="cgiar"></a>

### CGIAR Computer Vision for Crop Disease

**Source ID:** `CGIAR` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease)

Shadab Hussain (2020). [CGIAR Computer Vision for Crop Disease](https://www.kaggle.com/datasets/shadabhussain/cgiar-computer-vision-for-crop-disease). BibTeX: `shadabhussainCGIAR2020`.

The spreadsheet's paper URL mistakenly points to the AppleLeaf9 paper. This catalogue uses the CGIAR data-page citation from Table 1 and the manuscript bibliography.

<a id="appleleaf9"></a>

### AppleLeaf9

**Source ID:** `AppleLeaf9` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/JasonYangCode/AppleLeaf9/tree/main)

Yang, Qing and Duan, Shukai and Wang, Lidan (2022). [Efficient Identification of Apple Leaf Diseases in the Wild Using Convolutional Neural Networks](https://doi.org/10.3390/agronomy12112784). Agronomy. BibTeX: `yangEfficientIdentificationApple2022`.

<a id="bananaldi"></a>

### Banana Leaf Disease Images

**Source ID:** `BananaLDI` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/rjykr62kdh/1) · [Dataset DOI](https://doi.org/10.17632/rjykr62kdh.1)

Hailu, Yordanos (2021). [Banana Leaf Disease Images](https://data.mendeley.com/datasets/rjykr62kdh/1). Mendeley Data. BibTeX: `hailuBanana2021`.

<a id="atldsd"></a>

### Apple Tree Leaf Disease Segmentation Dataset

**Source ID:** `ATLDSD` · **Dataset license:** `unknown`

[Data / homepage](https://www.scidb.cn/en/detail?dataSetId=0e1f57004db842f99668d82183afd578&version=V1)

Feng, Jingze and Chao, Xiaofei (2022). [Apple Tree Leaf Disease Segmentation Dataset](https://doi.org/10.11922/sciencedb.01627). BibTeX: `fengApple2022`.

<a id="chilli"></a>

### chilli dataset

**Source ID:** `chilli` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/tf9dtfz9m6/2) · [Dataset DOI](https://doi.org/10.17632/tf9dtfz9m6.2)

Naik, B. Nageswararao and Malmathanraj, R. and Palanisamy, P. (2022). [Detection and Classification of Chilli Leaf Disease Using a Squeeze-and-Excitation-Based CNN Model](https://doi.org/10.1016/j.ecoinf.2022.101663). Ecol. Inf.. BibTeX: `naikDetection2022`.

Aishwarya M P and Padmanabha Reddy (2024). [chilli dataset](https://data.mendeley.com/datasets/tf9dtfz9m6/2). Mendeley Data. BibTeX: `aishwaryaChilliDeposit2024`.

The recorded download is Mendeley V2 (2024), deposited by Aishwarya M P and Padmanabha Reddy. The manuscript cites the Naik et al. (2022) article. The download-to-paper relationship is not established by the sparse deposit description; both are retained as recorded provenance.

<a id="cottonldd"></a>

### cotton leaf disease dataset

**Source ID:** `CottonLDD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/seroshkarim/cotton-leaf-disease-dataset)

Noon, Serosh Karim and Amjad, Muhammad and Ali Qureshi, Muhammad and Mannan, Abdul (2021). [Computationally Light Deep Learning Framework to Recognize Cotton Leaf Diseases](https://doi.org/10.3233/JIFS-210516). J. Intell. Fuzzy Syst.. BibTeX: `noonComputationally2021`.

<a id="cottonpd"></a>

### Cotton plant disease

**Source ID:** `CottonPD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease)

Dhamodharan R (2023). [Cotton Plant Disease](https://www.kaggle.com/datasets/dhamur/cotton-plant-disease). BibTeX: `dhamodharanrCotton2023`.

<a id="pld"></a>

### Potato Disease Leaf Dataset(PLD)

**Source ID:** `PLD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/rizwan123456789/potato-disease-leaf-datasetpld)

Rashid, Javed and Khan, Imran and Ali, Ghulam and Almotiri, Sultan H. and AlGhamdi, Mohammed A. and Masood, Khalid (2021). [Multi-Level Deep Learning Model for Potato Leaf Disease Recognition](https://doi.org/10.3390/electronics10172064). Electronics. BibTeX: `rashidMultilevelDeepLearning2021a`.

The historical spreadsheet reports 4,072 upstream images; the manuscript Table 1 reports 4,062. The released mapping independently records 1,020 selected images.

<a id="cassava"></a>

### Cassava Disease Classification

**Source ID:** `Cassava` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/c/cassava-disease/overview)

Mwebaze, Ernest and Gebru, Timnit and Frome, Andrea and Nsumba, Solomon and Tusubira, Jeremy (2019). [iCassava 2019 Fine-Grained Visual Categorization Challenge](https://doi.org/10.48550/arXiv.1908.02900). arXiv. BibTeX: `mwebazeICassava2019Finegrained2019`.

The retained URL and cited paper are the 2019 iCassava challenge. The catalogue reports 21,400 upstream images. An exact upstream archive version was not recorded; the manifest's filenames and selected 316 images define this release's membership.

<a id="pp2020"></a>

### Plant Pathology 2020 - FGVC7

**Source ID:** `PP2020` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/c/plant-pathology-2020-fgvc7/overview)

Thapa, Ranjita and Zhang, Kai and Snavely, Noah and Belongie, Serge and Khan, Awais (2020). [The Plant Pathology Challenge 2020 Data Set to Classify Foliar Disease of Apples](https://doi.org/10.1002/aps3.11390). Appl. Plant Sci.. BibTeX: `thapaPlant2020`.

<a id="esca"></a>

### ESCA-dataset

**Source ID:** `ESCA` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/89cnxc58kj/1) · [Dataset DOI](https://doi.org/10.17632/89cnxc58kj.1)

Alessandrini, M. and Calero Fuentes Rivera, R. and Falaschetti, L. and Pau, D. and Tomaselli, V. and Turchetti, C. (2021). [A Grapevine Leaves Dataset for Early Detection and Classification of Esca Disease in Vineyards through Machine Learning](https://doi.org/10.1016/j.dib.2021.106809). Data Brief. BibTeX: `alessandriniGrapevine2021`.

<a id="sugarcaneldd"></a>

### Sugarcane Leaf Disease Dataset

**Source ID:** `SugarcaneLDD` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/9424skmnrk/1) · [Dataset DOI](https://doi.org/10.17632/9424skmnrk.1)

Daphal, Swapnil and Koli, Sanjay (2022). [Sugarcane Leaf Disease Dataset](https://data.mendeley.com/datasets/9424skmnrk/1). Mendeley Data. BibTeX: `daphalSugarcane2022`.

<a id="cornld"></a>

### Corn Leaf Disease

**Source ID:** `CornLD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease)

Sandi Indika Saputra (2023). [Corn Leaf Disease](https://www.kaggle.com/datasets/ndisan/corn-leaf-disease). BibTeX: `sandiindikasaputraCorn2023`.

<a id="mangoleafbd"></a>

### Mango Leaf Disease Dataset

**Source ID:** `MangoLeafBD` · **Dataset license:** `CC-BY-NC-3.0`

[Data / homepage](https://data.mendeley.com/datasets/hxsnvwty3r/1) · [Dataset DOI](https://doi.org/10.17632/hxsnvwty3r.1)

Ahmed, Sarder Iftekhar and Ibrahim, Muhammad and Nadim, Md. and Rahman, Md. Mizanur and Shejunti, Maria Mehjabin and Jabid, Taskeed and Ali, Md. Sawkat (2023). [MangoLeafBD: A Comprehensive Image Dataset to Classify Diseased and Healthy Mango Leaves](https://doi.org/10.1016/j.dib.2023.108941). Data Brief. BibTeX: `ahmedMangoLeafBD2023`.

<a id="soybean-leaves"></a>

### Soybean images dataset

**Source ID:** `Soybean Leaves` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/bycbh73438/1) · [Dataset DOI](https://doi.org/10.17632/bycbh73438.1)

Mignoni, Maria Eloisa and Honorato, Aislan and Kunst, Rafael and Righi, Rodrigo and Massuquetti, Angélica (2022). [Soybean Images Dataset for Caterpillar and Diabrotica Speciosa Pest Detection and Classification](https://doi.org/10.1016/j.dib.2021.107756). Data Brief. BibTeX: `mignoniSoybean2022`.

<a id="sugarcanedd"></a>

### Sugarcane Disease Dataset

**Source ID:** `SugarcaneDD` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset)

Prabhakaran Soundar (2022). [Sugarcane Disease Dataset](https://www.kaggle.com/datasets/prabhakaransoundar/sugarcane-disease-dataset). BibTeX: `prabhakaransoundarSugarcane2022`.

<a id="coffee-plant-disease"></a>

### Coffee plant disease

**Source ID:** `Coffee plant disease` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease)

Coffee Disease (2021). [Coffee Plant Disease](https://www.kaggle.com/datasets/coffeedisease/coffee-plant-disease). BibTeX: `coffeediseaseCoffee2021`.

<a id="fruit-leaf"></a>

### Database of Leaf Images/Fruit Leaf

**Source ID:** `Fruit Leaf` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/hb74ynkjcn/4) · [Dataset DOI](https://doi.org/10.17632/hb74ynkjcn.4)

Chouhan, Siddharth Singh and Singh, Uday Pratap and Kaul, Ajay and Jain, Sanjeev (2019). [A Data Repository of Leaf Images: Practice towards Plant Conservation with Plant Pathology](https://doi.org/10.1109/ISCON47742.2019.9036158). 2019 4th International Conference on Information Systems and Computer Networks (ISCON). BibTeX: `chouhanDataRepositoryLeaf2019`.

<a id="weed25"></a>

### Weed25

**Source ID:** `Weed25` · **Dataset license:** `unknown`

[Data / homepage](https://pan.baidu.com/s/1rnUoDm7IxxmX1n1LmtXNXw) · [Project / recorded access page](https://doi.org/10.3389/fpls.2022.1053329)

Wang, Pei and Tang, Yin and Luo, Fan and Wang, Lihong and Li, Chengsong and Niu, Qi and Li, Hui (2022). [Weed25: A Deep Learning Dataset for Weed Identification](https://doi.org/10.3389/fpls.2022.1053329). Front. Plant Sci.. BibTeX: `wangWeed25DeepLearning2022`.

The paper supplies the Baidu download link and access code rn5h. The historical catalogue used the paper DOI as its data URL; both routes are retained here.

<a id="cottonweeddet12"></a>

### CottonWeedDet12

**Source ID:** `CottonWeedDet12` · **Dataset license:** `unknown`

[Data / homepage](https://weed-ai.sydney.edu.au/datasets/2c14915b-0827-4b65-9908-d2a6df0d48f3)

Dang, Fengying and Chen, Dong and Lu, Yuzhen and Li, Zhaojian (2023). [YOLOWeeds: A Novel Benchmark of YOLO Object Detectors for Multi-Class Weed Detection in Cotton Production Systems](https://doi.org/10.1016/j.compag.2023.107655). Comput. Electron. Agric.. BibTeX: `dangYOLOWeeds2023`.

<a id="deepweeds"></a>

### DeepWeeds

**Source ID:** `DeepWeeds` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/imsparsh/deepweeds)

Olsen, Alex and Konovalov, Dmitry A. and Philippa, Bronson and Ridd, Peter and Wood, Jake C. and Johns, Jamie and Banks, Wesley and Girgenti, Benjamin and Kenny, Owen and Whinney, James and Calvert, Brendan and Azghadi, Mostafa Rahimi and White, Ronald D. (2019). [DeepWeeds: A Multiclass Weed Species Image Dataset for Deep Learning](https://doi.org/10.1038/s41598-018-38343-3). Sci. Rep.. BibTeX: `olsenDeepWeeds2019`.

<a id="cwid15"></a>

### CottonWeedID15

**Source ID:** `CWID15` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/yuzhenlu/cottonweedid15)

Chen, Dong and Lu, Yuzhen and Li, Zhaojian and Young, Sierra (2022). [Performance Evaluation of Deep Transfer Learning on Multi-Class Identification of Common Weed Species in Cotton Production Systems](https://doi.org/10.1016/j.compag.2022.107091). Comput. Electron. Agric.. BibTeX: `chenPerformance2022`.

<a id="weednet-r"></a>

### SugarBeet2016

**Source ID:** `WeedNet-R` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/GOOJJJ/WeedNet-R/)

Guo, Zhiqiang and Goh, Hui Hwang and Li, Xiuhua and Zhang, Muqing and Li, Yong (2023). [WeedNet-R: A Sugar Beet Field Weed Detection Algorithm Based on Enhanced RetinaNet and Context Semantic Fusion](https://doi.org/10.3389/fpls.2023.1226329). Front. Plant Sci.. BibTeX: `guoWeedNetRSugarBeet2023`.

SugarBeet2016 in the catalogue corresponds to the WeedNet-R adapter and worksheet. The WeedNet-R repository acknowledges Sugar Beets 2016 as its upstream source. OpenPlant samples are object crops and can outnumber original images.

<a id="cwd30"></a>

### CWD30

**Source ID:** `CWD30` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/Mr-TalhaIlyas/CWD30) · [Project / recorded access page](https://github.com/mr-talhailyas/cwd30)

Ilyas, Talha and Arsa, Dewa Made Sri and Ahmad, Khubaib and Lee, Jonghoon and Won, Okjae and Lee, Hyeonsu and Kim, Hyongsuk and Park, Dong Sun (2025). [CWD30: A New Benchmark Dataset for Crop Weed Recognition in Precision Agriculture](https://doi.org/10.1016/j.compag.2024.109737). Comput. Electron. Agric.. BibTeX: `ilyasCWD302025`.

<a id="plantseedlings"></a>

### Plant Seedlings Classification

**Source ID:** `PlantSeedlings` · **Dataset license:** `CC-BY-SA-4.0`

[Data / homepage](https://vision.eng.au.dk/plant-seedlings-dataset/)

Giselsson, Thomas Mosgaard and Jørgensen, Rasmus Nyholm and Jensen, Peter Kryger and Dyrmann, Mads and Midtiby, Henrik Skov (2017). [A Public Image Database for Benchmark of Plant Seedling Classification Algorithms](https://doi.org/10.48550/arXiv.1711.05458). arXiv. BibTeX: `giselssonPublicImageDatabase2017`.

The adapter reads NonsegmentedV2 (cropped, nonsegmented single plants). Use the V2 link on the official dataset page.

<a id="plantnet-300k"></a>

### PlantNet-300K

**Source ID:** `plantnet_300K` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://zenodo.org/records/5645731) · [Dataset DOI](https://doi.org/10.5281/zenodo.5645731) · [Project / recorded access page](https://github.com/plantnet/PlantNet-300K) · [License declaration](https://api.datacite.org/dois/10.5281/zenodo.5645731)

Garcin, Camille and Joly, Alexis and Bonnet, Pierre and Affouard, Antoine and Jean-Christophe Lombardo and Chouet, Mathias and Servajean, Maximilien and Titouan Lorieul and Salmon, Joseph (2021). [Pl@ntNet-300K Image Dataset](https://doi.org/10.5281/ZENODO.5645731). Zenodo. BibTeX: `garcinPlntNet300KImageDataset2021`.

Garcin, Camille and Joly, Alexis and Bonnet, Pierre and Lombardo, Jean-Christophe and Affouard, Antoine and Chouet, Mathias and Servajean, Maximilien and Lorieul, Titouan and Salmon, Joseph (2021). [Pl@ntNet-300K: a plant image dataset with high label ambiguity and a long-tailed distribution](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/7e7757b1e12abcb736ab9a754ffb617a-Paper-round2.pdf). NeurIPS Datasets and Benchmarks. BibTeX: `garcinPlantNetPaper2021`.

The manuscript cites Zenodo record 5645731 (V1.1), whose DataCite record declares CC BY 4.0 at deposit level. The official repository also supplies the NeurIPS 2021 paper and per-image author/license metadata. Preserve those image-level terms. The 1,081 upstream labels correspond to 1,021 distinct class names in the released mapping after name standardization.

<a id="early-crop-weed"></a>

### early-crop-weed

**Source ID:** `Early_crop_weed` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/AUAgroup/early-crop-weed)

AUAgroup (2024). [AUAgroup/Early-Crop-Weed](https://github.com/AUAgroup/early-crop-weed). BibTeX: `auagroupAUAgroup2024`.

<a id="oppd"></a>

### Open Plant Phenotyping Database

**Source ID:** `OPPD` · **Dataset license:** `CC-BY-NC-SA-4.0`

[Data / homepage](https://vision.eng.au.dk/open-plant-phenotyping-database/)

Leminen Madsen, Simon and Mathiassen, Solvejg Kopp and Dyrmann, Mads and Laursen, Morten Stigaard and Paz, Laura-Carlota and Jørgensen, Rasmus Nyholm (2020). [Open Plant Phenotype Database of Common Weeds in Denmark](https://doi.org/10.3390/rs12081246). Remote Sens.. BibTeX: `leminenmadsenOpen2020`.

The upstream site describes 7,590 RGB images containing 315,038 plant objects. The catalogue's 315,038 therefore counts objects. OpenPlant uses selected individual-plant images recorded under images_plants.

<a id="cottonweeddet3"></a>

### CottonWeedDet3

**Source ID:** `CottonWeedDet3` · **Dataset license:** `unknown`

[Data / homepage](https://www.kaggle.com/datasets/yuzhenlu/cottonweeddet3)

Rahman, Abdur and Lu, Yuzhen and Wang, Haifeng (2023). [Performance Evaluation of Deep Learning Object Detectors for Weed Detection for Cotton](https://doi.org/10.1016/j.atech.2022.100126). Smart Agric. Technol.. BibTeX: `rahmanPerformance2023`.

Listed in the historical catalogue and manuscript Table 1, but no separately named worksheet or adapter registration occurs in the recovered release mapping/build registry. No contribution can be assigned from that evidence; the reason is unresolved.

<a id="weed-datasets"></a>

### weed-datasets

**Source ID:** `weed-datasets` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/zhangchuanyin/weed-datasets)

zhangchuanyin (2023). [Zhangchuanyin/Weed-Datasets](https://github.com/zhangchuanyin/weed-datasets). BibTeX: `zhangchuanyinZhangchuanyin2023`.

<a id="carrot-weed"></a>

### Carrot-Weed

**Source ID:** `Carrot-Weed` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/lameski/rgbweeddetection)

Lameski, Petre and Zdravevski, Eftim and Trajkovik, Vladimir and Kulakov, Andrea (2017). [Weed Detection Dataset with RGB Images Taken under Variable Light Conditions](https://doi.org/10.1007/978-3-319-67597-8_11). ICT Innovations 2017. BibTeX: `lameskiWeedDetectionDataset2017`.

Listed in the historical catalogue and manuscript Table 1, but no separately named worksheet or adapter registration occurs in the recovered release mapping/build registry. No contribution can be assigned from that evidence; the reason is unresolved.

<a id="vcd"></a>

### Vegetable Crops Dataset for Proximal Sensing (VCD)

**Source ID:** `VCD` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/d7kbzjr83k/1) · [Dataset DOI](https://doi.org/10.17632/d7kbzjr83k.1)

Lac, Louis and Keresztes, Barna and Louargant, Marine and Donias, Marc and Da Costa, Jean-Pierre (2022). [An Annotated Image Dataset of Vegetable Crops at an Early Stage of Growth for Proximal Sensing Applications](https://doi.org/10.1016/j.dib.2022.108035). Data Brief. BibTeX: `lacAnnotated2022`.

<a id="sorghumweed"></a>

### SorghumWeedDataset_Classification

**Source ID:** `SorghumWeed` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/4gkcyxjyss/1) · [Dataset DOI](https://doi.org/10.17632/4gkcyxjyss.1)

Justina, Michael J. and Thenmozhi, M. (2024). [SorghumWeedDataset_Classification and SorghumWeedDataset_Segmentation Datasets for Classification, Detection, and Segmentation in Deep Learning](https://doi.org/10.1016/j.dib.2023.109935). Data Brief. BibTeX: `justinaSorghumWeedDataset_Classification2024`.

Only the 1,404 sorghum samples are represented in the mapping; the upstream generic grasses/broad-leaf weed classes are not represented as separate OpenPlant taxa.

<a id="imageweeds"></a>

### ImageWeeds

**Source ID:** `ImageWeeds` · **Dataset license:** `CC-BY-4.0`

[Data / homepage](https://data.mendeley.com/datasets/8kjcztbjz2/2) · [Dataset DOI](https://doi.org/10.17632/8kjcztbjz2.2) · [License declaration](https://api.datacite.org/dois/10.17632/8kjcztbjz2.2)

Rai, Nitin and Mahecha, Maria Villamil and Christensen, Annika and Quanbeck, Jamison and Zhang, Yu and Howatt, Kirk and Ostlie, Michael and Sun, Xin (2023). [Multi-Format Open-Source Weed Image Dataset for Real-Time Weed Identification in Precision Agriculture](https://doi.org/10.1016/j.dib.2023.109691). Data Brief. BibTeX: `raiMultiformat2023`.

The recorded Mendeley V2 link returned a page without dataset metadata during review; its DataCite DOI record confirms the deposit and CC BY 4.0 declaration. Use the linked Data in Brief article for access information if the deposit page is unavailable.

<a id="tobset"></a>

### TobSet

**Source ID:** `TobSet` · **Dataset license:** `unknown`

[Data / homepage](https://github.com/mshahabalam/TobSet)

Alam, Muhammad Shahab and Alam, Mansoor and Tufail, Muhammad and Khan, Muhammad Umer and Güneş, Ahmet and Salah, Bashir and Nasir, Fazal E. and Saleem, Waqas and Khan, Muhammad Tahir (2022). [TobSet: A New Tobacco Crop and Weeds Image Dataset and Its Utilization for Vision-Based Spraying by Agricultural Robots](https://doi.org/10.3390/app12031308). Appl. Sci.. BibTeX: `alamTobSet2022`.

## Provenance

Counts are calculated from the 39 source worksheets in
`image_mapping_test_0220.xlsx`; the `datasets` summary worksheet is not counted a
second time. Names, links, and historical upstream sizes come from Sheet4 of
`datasets(已自动还原).xlsx`. Citation keys and bibliographic fields come from the
manuscript's `openplant.bib`, with separately identified primary-source additions.
The JSON includes SHA-256 hashes of these three source files. Historical catalogue
sizes are preserved as `catalogue_image_count`, not presented as currently verified
upstream sizes or OpenPlant contribution counts.

The source documentation can be regenerated without changing these inputs:

```bash
python tools/export_sources.py --catalogue /path/to/catalogue.xlsx \
  --mapping /path/to/image_mapping_test_0220.xlsx \
  --bibliography /path/to/openplant.bib --output . --verify-dois
```

The `--verify-dois` option checks supported article DOIs through Crossref. Other
verification and dataset-license evidence is recorded from the primary pages
reviewed for this release.
