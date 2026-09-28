def loading_workbook(name):
    return f"Loading analysis-ready dataset: {name}"


def workbook_not_found(path):
    return f"Input workbook not found: {path}"


def sheets_missing(missing):
    return f"Analysis-ready dataset is missing required sheets: {missing}"


def workbook_loaded(name):
    return f"Workbook: {name}"


def sheets_read(count):
    return f"Sheets read: {count}"


def sheet_size(rows, columns):
    return f"Rows: {rows}  Columns: {columns}"


def more_columns(count):
    return f"... {count} more columns"


def analysis_ready_description():
    return "Create analysis-ready tables from the analysis-ready dataset"


def data_argument_help():
    return "Path to the analysis-ready dataset workbook"


def loading_configuration(path):
    return f"Loading analysis configuration: {path}"


def configuration_not_found(path):
    return f"Analysis configuration not found: {path}"


def sheets_loaded(count):
    return f"Loaded {count} source sheets"


def building_tables():
    return "Building analysis-ready tables"


def tables_built(count):
    return f"Built {count} analysis-ready tables"


def writing_table(index, total, name, rows):
    return f"[{index}/{total}] Writing {name} ({rows} rows)"


def writing_workbook(path):
    return f"Writing combined workbook: {path}"


def running_validation():
    return "Running validation"


def phase_complete():
    return "Analysis-ready tables complete"


def source_studies(count):
    return f"Source studies: {count}"


def barrier_mitigation_rows(count):
    return f"Barrier-mitigation rows: {count}"


def exact_linked_rows(count):
    return f"Linked performance rows: {count}"


def validation_status(status):
    return f"Validation status: {status}"


def output_workbook(path):
    return f"Output workbook: {path}"


def csv_directory(path):
    return f"CSV directory: {path}"


def validation_failed(path):
    return f"Validation failed. Inspect {path}"


def phase_started(name):
    return f"{name} started"


def progress_log(path):
    return f"Progress log: {path}"


def study_master_row_mismatch():
    return "Study master does not preserve one row per identification record"


def study_master_duplicate():
    return "Study master contains duplicate Study IDs"


def quality_duplicate():
    return "Evidence quality contains duplicate Study IDs"


def no_exact_comparisons():
    return "No exact baseline-mitigation performance comparisons were created"


def cannot_serialize(kind):
    return f"Cannot serialize {kind}"


def tables_missing(names):
    return (
        f"Analysis-ready tables are missing: {names}. "
        "Run src/01_create_analysis_ready_tables.py first."
    )


def register_rows(count):
    return f"Comparison register rows: {count}"


def eligible_rows(count):
    return f"Eligible performance rows: {count}"


def pending_rows(count):
    return f"Pending register rows: {count}"


def removed_previous_table(name):
    return f"Removed previous table: {name}"


def register_count_mismatch():
    return "Comparison register does not preserve one row per baseline context"


def register_duplicate():
    return "Comparison register contains duplicate baseline contexts"


def pending_remain():
    return "Comparison register contains pending rows"


def gain_mismatch():
    return "An eligible gain does not equal selected percent minus baseline percent"


def audit_count_mismatch():
    return "Performance linkage audit does not preserve every mitigation result"


def quality_row_mismatch():
    return "Evidence quality does not preserve one row per identification record"


def profile_count_mismatch():
    return "Barrier or mitigation profile does not preserve the coding records"


def register_status_unknown():
    return "A register row has a status other than Eligible, Ineligible, or Pending"


def selected_result_reused():
    return "A tab 8 result row is selected for more than one baseline context"


def performance_not_eligible():
    return "Performance results include a comparison that is not eligible"


def statistics_description():
    return "Create statistics tables from the analysis-ready tables"


def loading_analysis_ready(path):
    return f"Loading analysis-ready tables: {path}"


def building_statistics():
    return "Building statistics tables"


def statistics_complete():
    return "Statistics tables complete"


def statistics_run_complete():
    return "Statistics run complete"


def task_synthesis(task, studies, median):
    return f"{task}: {studies} studies, median gain {median}"


def negative_gains_missing():
    return "Selected gains do not include a negative gain"


def rq6_strategy_mismatch():
    return "A synthetic-method comparison includes a paper with several mitigation strategies"


def study_gain_count_mismatch():
    return "Study-level gains do not match the selected comparisons"


def synthesis_invalid():
    return "Task synthesis is missing a task or labels a gain as meaningful"


def metric_mismatch():
    return "A selected comparison uses a metric outside Detection mAP@0.5, Classification Accuracy, or Segmentation mIoU"


def bootstrap_setting_unsupported():
    return "Bootstrap settings must use the median and the percentile interval"


def question_map_mismatch():
    return "The research-question map does not list each statistics table once"


def statistics_studies(count):
    return f"Study-level gains: {count}"


def figures_description():
    return "Create figures from the saved statistics"


def building_figures():
    return "Building figures"


def figures_run_complete():
    return "Figures run complete"


def figures_directory(path):
    return f"Figures directory: {path}"


def writing_figure(index, total, name):
    return f"[{index}/{total}] Writing {name}"


def map_not_found(path):
    return f"World map not found: {path}"


def unmatched_countries(names):
    return f"Countries not matched to the map: {names}"


def figure_missing():
    return "A configured figure file was not written"


def figure_map_mismatch():
    return "The research-question map names a figure that is not configured"
