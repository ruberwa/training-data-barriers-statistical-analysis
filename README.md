# Training Data Barriers and Mitigation Strategies in Weed Detection, Classification, and Segmentation: A Systematic Review and Quantitative Synthesis

Repository: `training-data-barriers-statistical-analysis`

Statistical analysis and reproducibility materials for this systematic review and quantitative synthesis.

The scripts only read the source workbook. The first script writes the analysis-ready tables. The second script reads those tables and writes the statistics. The third script reads the statistics and draws the figures. Each script leaves the earlier files as they are.

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

Python 3.12 or newer is required. Operating-system installers are in [Docs/02_Installation.md](Docs/02_Installation.md). From the project root, create the virtual environment, install the packages, then run the three scripts in this order. Each script prints `Validation status: PASS` when that step is good. Start the next script only after that line appears.

macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

1. Build the analysis-ready tables from the source workbook.

```bash
python3 src/01_create_analysis_ready_tables.py
```

Tables are written to `results/analysis_ready_tables/`.

2. Build the statistics from those tables.

```bash
python3 src/02_create_statistical_results.py
```

Tables are written to `results/statistics/`.

3. Draw the figures from the saved statistics.

```bash
MPLCONFIGDIR="results/.mplconfig" python3 src/03_create_figures.py
```

On Windows PowerShell, set the variable first:

```powershell
$env:MPLCONFIGDIR = "results/.mplconfig"
python3 src/03_create_figures.py
```

Figures are written to `results/figures/pdf/`, `results/figures/png/`, and `results/figures/tiff/`. The pass or fail record for each step is in `results/validation/`.

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
