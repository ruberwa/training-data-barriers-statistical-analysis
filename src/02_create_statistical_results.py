from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from common.Messages import (
    building_statistics,
    csv_directory,
    loading_analysis_ready,
    loading_configuration,
    output_workbook,
    statistics_run_complete,
    phase_started,
    progress_log,
    removed_previous_table,
    running_validation,
    statistics_complete,
    statistics_description,
    statistics_studies,
    task_synthesis,
    validation_failed,
    validation_status,
    writing_table,
    writing_workbook,
)
from common.paths import (
    ANALYSIS_CONFIG,
    ANALYSIS_READY_CSV_DIR,
    BOOTSTRAP_CONFIG,
    LOGS_DIR,
    RESEARCH_QUESTION_MAP,
    STATISTICS_CSV_DIR,
    STATISTICS_DIR,
    VALIDATION_DIR,
)
from src.analysis.statistical_pipeline import run_all_statistics
from utils.io import ensure_directories, load_analysis_ready, load_yaml, save_csv, save_json
from utils.progress import open_log, record
from utils.validation import statistics_validation


def _sheet_name(key, used):
    name = key[:31]
    if name not in used:
        used.add(name)
        return name
    index = 2
    while True:
        suffix = f"_{index}"
        candidate = f"{key[:31 - len(suffix)]}{suffix}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        index += 1


def main() -> None:
    parser = argparse.ArgumentParser(description=statistics_description())
    parser.add_argument("--tables", default=str(ANALYSIS_READY_CSV_DIR))
    args = parser.parse_args()

    tables_dir = Path(args.tables).resolve()
    ensure_directories(STATISTICS_DIR, STATISTICS_CSV_DIR, VALIDATION_DIR, LOGS_DIR)
    log_path = LOGS_DIR / "statistics.log"
    open_log(log_path)
    lines = []

    def note(message: str) -> None:
        lines.append(message)
        record(log_path, message)

    note(phase_started(statistics_description()))
    note(progress_log(log_path))
    note(loading_configuration(ANALYSIS_CONFIG))
    note(loading_configuration(BOOTSTRAP_CONFIG))
    note(loading_configuration(RESEARCH_QUESTION_MAP))
    cfg = load_yaml(ANALYSIS_CONFIG)
    cfg["bootstrap"] = load_yaml(BOOTSTRAP_CONFIG)
    question_map = load_yaml(RESEARCH_QUESTION_MAP)
    note(loading_analysis_ready(tables_dir))
    frames = load_analysis_ready(tables_dir)
    note(building_statistics())
    tables = run_all_statistics(frames, cfg)
    ordered = {}
    for section in question_map.values():
        for name in section["statistical_tables"]:
            if name in tables:
                ordered[name] = tables.pop(name)
    ordered.update(tables)
    tables = ordered
    note(statistics_complete())

    total_tables = len(tables)
    for index, (key, frame) in enumerate(tables.items(), start=1):
        output_path = STATISTICS_CSV_DIR / f"{key}.csv"
        note(writing_table(index, total_tables, output_path.name, len(frame)))
        save_csv(frame, output_path)

    written = {f"{key}.csv" for key in tables}
    for previous in STATISTICS_CSV_DIR.glob("*.csv"):
        if previous.name not in written:
            previous.unlink()
            note(removed_previous_table(previous.name))

    workbook_path = STATISTICS_DIR / "statistics.xlsx"
    note(writing_workbook(workbook_path))
    used_names = set()
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        for key, frame in tables.items():
            frame.to_excel(writer, sheet_name=_sheet_name(key, used_names), index=False)

    note(running_validation())
    validation = statistics_validation(frames, tables, cfg, question_map)
    validation["source_directory"] = str(tables_dir)
    validation_path = VALIDATION_DIR / "statistics.json"
    save_json(validation, validation_path)

    note(statistics_run_complete())
    note(statistics_studies(len(tables["rq3_study_gains"])))
    for _, row in tables["rq3_task_synthesis"].iterrows():
        note(task_synthesis(row["Task"], int(row["Studies"]), row["Median gain (pp)"]))
    note(validation_status(validation["status"]))
    note(output_workbook(workbook_path))
    note(csv_directory(STATISTICS_CSV_DIR))
    sys.stdout.write("\n".join(lines) + "\n")
    if validation["status"] != "PASS":
        raise SystemExit(validation_failed(validation_path))


if __name__ == "__main__":
    main()
