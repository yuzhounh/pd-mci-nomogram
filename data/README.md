# Data Directory

This repository does not include raw PPMI data or participant-level derived files.

## Required Input File

Obtain the following file from the [PPMI data portal](https://www.ppmi-info.org/access-data-specimens/download-data) (RRID:SCR_006431) after completing PPMI registration and accepting the Data Use Agreement:

- `PPMI_Curated_Data_Cut_Public_20260810.xlsx`

## Placement

Choose either option:

1. Copy `PPMI_Curated_Data_Cut_Public_20260810.xlsx` into `data/raw/` inside this repository (ignored by `.gitignore`).
2. Keep the file in a shared external folder and set the environment variable `PPMI_DATA_DIR` to that folder before running `python run_all.py`.

Cohort assertions in `step_01_extract_data.py` verify the recorded 10 August 2026 cut (8,546 PD visits across 1,684 participants).
