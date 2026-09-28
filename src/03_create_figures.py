from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg", force=True)

from common.Messages import (
    building_figures,
    figures_description,
    figures_run_complete,
    loading_configuration,
    figures_directory,
    phase_started,
    progress_log,
    running_validation,
    validation_failed,
    validation_status,
    writing_figure,
)
from common.paths import (
    ANALYSIS_CONFIG,
    ANALYSIS_READY_CSV_DIR,
    BOOTSTRAP_CONFIG,
    FIGURES_CONFIG,
    FIGURES_DIR,
    LOGS_DIR,
    RESEARCH_QUESTION_MAP,
    STATISTICS_CSV_DIR,
    VALIDATION_DIR,
)
from src.analysis.figures import create_all_figures
from utils.io import ensure_directories, load_figure_config, load_yaml, save_json
from utils.plotting import setup_style
from utils.progress import open_log, record
from utils.validation import figures_validation


def main() -> None:
    parser = argparse.ArgumentParser(description=figures_description())
    parser.add_argument("--statistics", default=str(STATISTICS_CSV_DIR))
    parser.add_argument("--tables", default=str(ANALYSIS_READY_CSV_DIR))
    args = parser.parse_args()

    statistics_dir = Path(args.statistics).resolve()
    tables_dir = Path(args.tables).resolve()
    ensure_directories(FIGURES_DIR, VALIDATION_DIR, LOGS_DIR)
    log_path = LOGS_DIR / "figures.log"
    open_log(log_path)
    lines = []

    def note(message: str) -> None:
        lines.append(message)
        record(log_path, message)

    note(phase_started(figures_description()))
    note(progress_log(log_path))
    note(loading_configuration(FIGURES_CONFIG / "common.yaml"))
    for path in sorted(FIGURES_CONFIG.glob("*.yaml")):
        if path.name != "common.yaml":
            note(loading_configuration(path))
    note(loading_configuration(ANALYSIS_CONFIG))
    note(loading_configuration(BOOTSTRAP_CONFIG))
    note(loading_configuration(RESEARCH_QUESTION_MAP))
    fig_cfg = load_figure_config(FIGURES_CONFIG)
    analysis_cfg = load_yaml(ANALYSIS_CONFIG)
    analysis_cfg["bootstrap"] = load_yaml(BOOTSTRAP_CONFIG)
    question_map = load_yaml(RESEARCH_QUESTION_MAP)
    setup_style(fig_cfg)
    note(building_figures())
    outputs, notes_from_figures = create_all_figures(statistics_dir, tables_dir, FIGURES_DIR, fig_cfg, analysis_cfg)
    for message in notes_from_figures:
        note(message)
    names = []
    for path in outputs:
        if path.stem not in names:
            names.append(path.stem)
    for index, name in enumerate(names, start=1):
        note(writing_figure(index, len(names), name))
    note(running_validation())
    validation = figures_validation(fig_cfg, question_map, FIGURES_DIR)
    validation["source_directory"] = str(statistics_dir)
    validation["files"] = [str(path) for path in outputs]
    validation_path = VALIDATION_DIR / "figures.json"
    save_json(validation, validation_path)
    note(figures_run_complete())
    note(validation_status(validation["status"]))
    note(figures_directory(FIGURES_DIR))
    sys.stdout.write("\n".join(lines) + "\n")
    if validation["status"] != "PASS":
        raise SystemExit(validation_failed(validation_path))


if __name__ == "__main__":
    main()
