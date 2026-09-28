**Title:** Build the statistics tables

## What this step does
- Reads the analysis-ready tables
- Leaves those tables unchanged
- Writes one workbook and one CSV for each statistics table

## Run
- From the project root, after the analysis-ready tables: `python3 src/02_create_statistical_results.py`

## Settings
- Task metrics in `config/analysis-config.yaml`: Detection `mAP@0.5`, Classification `Accuracy`, Segmentation `mIoU`
- Bootstrap settings in `config/bootstrap-config.yaml`: seed, repetitions, permutation repetitions, median, and the percentile interval
- `config/research-question-map.yaml` lists the statistics table for each research question
- A 10-point gain is not labeled meaningful

## What each question uses
- **Evidence profile:** year, task, environment, country, and dataset size. Dataset size uses `Dataset Size (numeric)` only
- **RQ1:** barrier prevalence by task, and a study-preserving permutation test of the barrier profiles
- **RQ2:** mitigation prevalence by task. The barrier–mitigation table counts strategies that occur in the same paper. Same-instance rows stay labeled as co-occurrence. The permutation test uses each paper’s barrier profile and mitigation profile
- **RQ3:** one signed gain per paper. For each task, the number of papers, the median gain, and the bootstrap interval. Negative gains stay in
- **RQ4:** that gain against baseline percent, log dataset size when the number is clear, environment, and the paper’s barrier and mitigation profile. A subgroup needs at least 5 papers. A regression needs at least 10
- **RQ5:** the quality profile, the sensitivity scenarios that still apply, and leave-one-paper-out on the task medians. There is no within-paper mean scenario
- **RQ6:** Synthetic Image Methods against other methods after baseline and task. A paper enters only when its mitigation profile has one strategy. Data Augmentation and Synthetic Data Generation remain the two synthetic subtypes

## Where they are written
- `results/statistics/statistics.xlsx`
- `results/statistics/csv/`
- `results/logs/statistics.log`
- `results/validation/statistics.json`
