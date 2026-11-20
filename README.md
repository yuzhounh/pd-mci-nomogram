# PD-MCI Nomogram

Analysis code and browser-based calculator for estimating the probability of concurrent test-defined mild cognitive impairment in Parkinson's disease (PD-MCI) without cognitive-test inputs.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Paper:** Jing Wang, Yanfang Chen, Kunpeng Xia, Xiao Xie, Hongfang Han, and Li Zhang. *Predicting Concurrent Test-Defined Mild Cognitive Impairment in Parkinson's Disease Using Non-Cognitive Predictors*.

- **Online calculator:** [https://yuzhounh.github.io/pd-mci-nomogram/](https://yuzhounh.github.io/pd-mci-nomogram/)

## Overview

Using the Parkinson's Progression Markers Initiative (PPMI) curated data cut of 10 August 2026, this workflow performs subject-level training/validation splitting, time-aware predictor imputation, LASSO feature selection, unpenalized logistic regression with patient-clustered standard errors, comparison against eight machine-learning benchmarks (CatBoost, EasyEnsemble, LightGBM, tuned LR, MLP, RF, SVM, XGBoost), patient-cluster bootstrap confidence intervals, comparative ROC/PR plotting, and R nomogram rendering.

The final six-predictor model uses sex, years of education (capped at 20 in PPMI), 15-item Geriatric Depression Scale (GDS-15) score, Hoehn and Yahr (H&Y) stage, five-item postural instability and gait difficulty (PIGD) subscore mean, and Movement Disorder Society-Sponsored Revision of the Unified Parkinson's Disease Rating Scale Part III (MDS-UPDRS III) score (OFF-medication in treated participants or untreated assessments).

## Data Access and Setup

Raw PPMI data and participant-level derived datasets are not distributed in this repository. Authorized researchers can obtain `PPMI_Curated_Data_Cut_Public_20260810.xlsx` from the [PPMI data portal](https://www.ppmi-info.org/access-data-specimens/download-data) (RRID:SCR_006431) under the PPMI Data Use Agreement.

Place the workbook in `data/raw/` (ignored by Git), or point the `PPMI_DATA_DIR` environment variable to a shared directory containing the file:

```bash
export PPMI_DATA_DIR=/path/to/ppmi/curated   # PowerShell: $env:PPMI_DATA_DIR = 'D:\path\to\ppmi\curated'
```

See [data/README.md](data/README.md) for details.

## Environment and Usage

The recorded environment uses Python 3.13.5 (dependencies pinned in [requirements.txt](requirements.txt)) and R 4.6.1 with `rms` 8.1.1 and `jsonlite` 2.0.0 (`pdfcrop` optional).

```bash
python -m pip install -r requirements.txt
python run_all.py --dry-run
python run_all.py
```

`run_all.py` executes the 24-script Python/R workflow in dependency order and supports `--python-only`, `--r-only`, `--start-from`, and `--skip`.

### Run the Web Calculator Locally

`index.html` runs directly in the browser using the frozen full-precision coefficients in [model_parameters.json](model_parameters.json) (no PPMI data or Python packages required):

```bash
python -m http.server 8000
```

Then open [http://localhost:8000/](http://localhost:8000/).

## Repository Structure

```text
pd-mci-nomogram/
├── README.md                    # Project overview and usage
├── LICENSE                      # MIT license
├── CITATION.cff                 # Citation metadata
├── index.html                   # GitHub Pages web calculator
├── model_parameters.json        # Frozen six-predictor model coefficients and thresholds
├── requirements.txt             # Pinned Python dependencies
├── run_all.py                   # Pipeline runner
├── step_01_*.py ... step_17_*.py# Primary data preparation, modeling, and evaluation scripts
├── step_16_nomogram.R           # R nomogram script
├── utils.py / figstyle.py       # Shared evaluation and plotting utilities
├── PPMI_*feature*.csv           # Non-participant feature configuration tables
└── data/
    └── README.md                # Data placement instructions
```

## License and Contact

Released under the [MIT License](LICENSE). PPMI data remain subject to the PPMI Data Use Agreement.

Correspondence: Jing Wang (`wangjing@xynu.edu.cn`).
