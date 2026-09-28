**Title:** Build the figures

## What this step does
- Reads the saved statistics
- Leaves those tables unchanged
- Draws one figure for the evidence profile and one figure for each research question

## Run
- From the project root, after the statistics: `python3 src/03_create_figures.py`

## Settings
- Shared colors, cards, grids, and file types are in `config/figures/common.yaml`. Each figure has its own file in `config/figures/`
- A category appears when it has at least 5 studies
- `config/research-question-map.yaml` names the figure for each question

## What each figure shows
- **Evidence profile:** publication year by task, dataset size from `Dataset Size (numeric)`, and the country map
- **RQ1:** barrier types colored by category, each with its study count and percent, a pie of category records, and task dots for each type
- **RQ2:** mitigation strategies colored by category, each with its study count and percent, a pie of category records, and a same-paper heatmap of barrier type by mitigation strategy
- **RQ3:** one signed gain per paper. The summary mark is the task median and its bootstrap interval
- **RQ4:** that gain against baseline percent, log dataset size, and environment. A regression line is drawn when the task has at least 10 papers
- **RQ5:** a heatmap of quality judgments, with the percent of studies, and a sensitivity forest by task with the study count beside each row. There is no within-paper mean scenario
- **RQ6:** one forest. The adjusted synthetic contrast has its interval. A subtype is a point with its study count and no interval. Each task’s synthetic median has its interval. The contrast uses papers with one mitigation strategy

## Where they are written
- `results/figures/pdf/`
- `results/figures/png/`
- `results/figures/tiff/`
- `results/logs/figures.log`
- `results/validation/figures.json`
