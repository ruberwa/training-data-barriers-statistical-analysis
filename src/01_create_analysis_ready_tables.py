from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from common.constants import ANALYSIS_READY_SHEETS, STATUS_PENDING
from common.Messages import (
    building_tables,
    csv_directory,
    data_argument_help,
    eligible_rows,
    loading_configuration,
    loading_workbook,
    output_workbook,
    pending_rows,
    analysis_ready_description,
    phase_complete,
    phase_started,
    progress_log,
    register_rows,
    removed_previous_table,
    running_validation,
    sheets_loaded,
    source_studies,
    tables_built,
    validation_failed,
    validation_status,
    writing_table,
    writing_workbook,
)
from common.paths import (
    ANALYSIS_CONFIG,
    ANALYSIS_READY_CSV_DIR,
    ANALYSIS_READY_DIR,
    DATA_FILE,
    LOGS_DIR,
    VALIDATION_DIR,
)
from src.analysis.prepare_tables import build_analysis_ready
from utils.io import ensure_directories, load_yaml, read_raw_ard, save_csv, save_json, sha256
from utils.progress import open_log, record
from utils.validation import analysis_ready_validation


def main() -> None:
    parser = argparse.ArgumentParser(description=analysis_ready_description())
    parser.add_argument("--data", default=str(DATA_FILE), help=data_argument_help())
    args = parser.parse_args()

    data_path = Path(args.data).resolve()
    ensure_directories(ANALYSIS_READY_DIR, ANALYSIS_READY_CSV_DIR, VALIDATION_DIR, LOGS_DIR)
    log_path = LOGS_DIR / "analysis_ready_tables.log"
    open_log(log_path)
    lines = []

    def note(message: str) -> None:
        lines.append(message)
        record(log_path, message)

    note(phase_started(analysis_ready_description()))
    note(progress_log(log_path))
    note(loading_configuration(ANALYSIS_CONFIG))
    cfg = load_yaml(ANALYSIS_CONFIG)
    note(loading_workbook(data_path.name))
    raw = read_raw_ard(data_path)
    note(sheets_loaded(len(raw)))
    note(building_tables())
    ready = build_analysis_ready(raw)
    note(tables_built(len(ready)))

    total_tables = len(ready)
    for index, (key, frame) in enumerate(ready.items(), start=1):
        output_path = ANALYSIS_READY_CSV_DIR / f"{key}.csv"
        note(writing_table(index, total_tables, output_path.name, len(frame)))
        save_csv(frame, output_path)

    written = {f"{key}.csv" for key in ready}
    for previous in ANALYSIS_READY_CSV_DIR.glob("*.csv"):
        if previous.name not in written:
            previous.unlink()
            note(removed_previous_table(previous.name))

    workbook_path = ANALYSIS_READY_DIR / "analysis_ready_tables.xlsx"
    note(writing_workbook(workbook_path))
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        for key, frame in ready.items():
            frame.to_excel(writer, sheet_name=ANALYSIS_READY_SHEETS[key], index=False)

    note(running_validation())
    validation = analysis_ready_validation(raw, ready)
    validation["source_file"] = str(data_path)
    validation["source_sha256"] = sha256(data_path)
    validation["expected_studies_from_config"] = cfg["project"].get("expected_studies")
    validation_path = VALIDATION_DIR / "analysis_ready_tables.json"
    save_json(validation, validation_path)

    note(phase_complete())
    note(source_studies(ready["study_master"]["Study ID"].nunique()))
    note(register_rows(len(ready["comparison_register"])))
    note(eligible_rows(len(ready["performance_results"])))
    note(pending_rows(int(ready["comparison_register"]["Status"].eq(STATUS_PENDING).sum())))
    note(validation_status(validation["status"]))
    note(output_workbook(workbook_path))
    note(csv_directory(ANALYSIS_READY_CSV_DIR))
    sys.stdout.write("\n".join(lines) + "\n")
    if validation["status"] != "PASS":
        raise SystemExit(validation_failed(validation_path))


if __name__ == "__main__":
    main()
