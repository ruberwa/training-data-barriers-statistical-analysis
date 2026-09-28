**Title:** Build the analysis-ready tables

## What this step does
- Reads `data/Ready Analysis dataset.xlsx`
- Turns the numbered source sheets into the analysis-ready tables
- Leaves the source workbook unchanged

## Run
- From the project root: `python3 src/01_create_analysis_ready_tables.py`

## Tables
- **Study Master:** one row per study, with task, environment, year, and dataset size
- **Barrier Profile:** each coded barrier, with the study task
- **Mitigation Profile:** each coded mitigation, with the study task
- **Co-occurrence:** same instance ID within a paper
- **Comparison Register:** one row per baseline context
- **Performance Results:** eligible comparisons, with the signed gain
- **Performance Linkage Audit:** every mitigation result
- **Evidence Quality:** risk-of-bias and credibility judgments for each study

## Where they are written
- `results/analysis_ready_tables/analysis_ready_tables.xlsx`
- `results/analysis_ready_tables/csv/study_master.csv`
- `results/analysis_ready_tables/csv/barrier_profile.csv`
- `results/analysis_ready_tables/csv/mitigation_profile.csv`
- `results/analysis_ready_tables/csv/barrier_mitigation_cooccurrence.csv`
- `results/analysis_ready_tables/csv/comparison_register.csv`
- `results/analysis_ready_tables/csv/performance_results.csv`
- `results/analysis_ready_tables/csv/performance_linkage_audit.csv`
- `results/analysis_ready_tables/csv/evidence_quality.csv`
- `results/logs/analysis_ready_tables.log`
- `results/validation/analysis_ready_tables.json`
