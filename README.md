# training-data-barriers-statistical-analysis

Statistical analysis and reproducibility materials for the systematic review of training-data barriers and mitigation strategies in weed computer vision.

The source workbook stays unchanged. Each later step reads the previous output and leaves it in place. Running a script is what produces the tables and figures.

## Questions

- **Evidence profile:** publication year, task, environment, country, and dataset size
- **RQ1:** which training-data barriers are reported, and how their profiles differ across Detection, Segmentation, and Classification
- **RQ2:** which mitigation strategies are used with those barriers, and which barrier–strategy pairs occur in the same paper
- **RQ3:** what performance change is reported with mitigation, as one signed gain per paper within each task
- **RQ4:** how far barrier, mitigation, baseline performance, environment, and dataset size account for differences in that gain
- **RQ5:** how robust the findings are under the credibility checks that still apply
- **RQ6:** whether Synthetic Image Methods differ from other single-strategy methods after baseline and task

Task order is Detection, Segmentation, Classification. The task metrics are Detection `mAP@0.5`, Segmentation `mIoU`, and Classification `Accuracy`. Gains are in percentage points. Intervals use the median and a percentile bootstrap.

## Run

Install Python 3.12 or newer and the project packages first. The steps are in [Docs/02_Installation.md](Docs/02_Installation.md). Activate the virtual environment, then run these from the project root. Wait for `Validation status: PASS` before the next command.

```bash
python3 src/01_create_analysis_ready_tables.py
```

```bash
python3 src/02_create_statistical_results.py
```

```bash
MPLCONFIGDIR="results/.mplconfig" python3 src/03_create_figures.py
```

## Layout

- `data/Ready Analysis dataset.xlsx`: source record of the included studies
- `data/maps/`: country boundaries for the geographic figure
- `config/analysis-config.yaml`: task order, metrics, and sensitivity rules
- `config/bootstrap-config.yaml`: bootstrap seed, repetitions, and the percentile interval
- `config/research-question-map.yaml`: which statistics tables and figures belong to each question
- `config/figures/common.yaml`: colors, cards, grids, and file types shared by every figure
- `config/figures/`: one settings file per figure
- `src/01_create_analysis_ready_tables.py`: workbook to analysis-ready tables
- `src/02_create_statistical_results.py`: analysis-ready tables to statistics
- `src/03_create_figures.py`: saved statistics to figures
- `results/`: tables, statistics, figures, logs, and validation records written by those scripts

## Documents

- [Docs/01_Project-Setup.md](Docs/01_Project-Setup.md): what is in the repository
- [Docs/02_Installation.md](Docs/02_Installation.md): Python and project packages
- [Docs/03_Analysis-Ready-Tables.md](Docs/03_Analysis-Ready-Tables.md): how the workbook becomes the analysis-ready tables
- [Docs/04_Statistics.md](Docs/04_Statistics.md): how those tables become the research-question statistics
- [Docs/05_Figures.md](Docs/05_Figures.md): how the saved statistics become the figures
