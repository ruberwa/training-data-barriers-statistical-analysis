# Training Data Barriers and Mitigation Strategies in Weed Detection, Classification, and Segmentation: A Systematic Review and Quantitative Synthesis

Statistical analysis and reproducibility materials for this systematic review and quantitative synthesis.

Three scripts run in order. The first reads the source workbook and writes the analysis-ready tables. The second reads those tables and writes the statistics. The third reads the statistics and draws the figures. Each script leaves the earlier files as they are. A step is ready for the next script when it prints `Validation status: PASS`.

## Get the repository

Clone it, then move into the project folder:

```bash
git clone https://github.com/ruberwa/training-data-barriers-statistical-analysis.git
cd training-data-barriers-statistical-analysis
```

Or download the ZIP from [the repository page](https://github.com/ruberwa/training-data-barriers-statistical-analysis): **Code → Download ZIP**, unpack it, and open that folder. Every path below is from that folder.

## Where to look

- **Dataset:** `data/Ready Analysis dataset.xlsx`. This workbook is in the clone and in the ZIP. It is the source record of the included studies. The first script reads it.
- **Figures:** `results/figures/`. PDF, PNG, and TIFF copies are in `results/figures/pdf/`, `results/figures/png/`, and `results/figures/tiff/`. These folders appear after the third script runs. They are not in the clone or the ZIP.
- `config/`: task metrics, bootstrap settings, and figure settings
- `src/`: the three scripts, in the order under Run
- `Docs/`: what each stage does and how the numbers are produced
- `results/`: tables, statistics, figures, logs, and validation records written by the scripts

## Run

Python 3.12 or newer is required. Operating-system installers are in [Docs/02_Installation.md](Docs/02_Installation.md). From the project root, create the virtual environment and install the packages.

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

1. Build the analysis-ready tables.

```bash
python3 src/01_create_analysis_ready_tables.py
```

2. Build the statistics from those tables.

```bash
python3 src/02_create_statistical_results.py
```

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

## Documents

- [Docs/01_Project-Setup.md](Docs/01_Project-Setup.md): what is in the repository
- [Docs/02_Installation.md](Docs/02_Installation.md): Python and project packages
- [Docs/03_Analysis-Ready-Tables.md](Docs/03_Analysis-Ready-Tables.md): how the workbook becomes the analysis-ready tables
- [Docs/04_Statistics.md](Docs/04_Statistics.md): how those tables become the statistics
- [Docs/05_Figures.md](Docs/05_Figures.md): how the saved statistics become the figures
