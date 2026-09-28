from __future__ import annotations

import pandas as pd

from common.constants import STATUS_ELIGIBLE, STATUS_INELIGIBLE, STATUS_PENDING
from common.Messages import (
    audit_count_mismatch,
    bootstrap_setting_unsupported,
    figure_map_mismatch,
    figure_missing,
    gain_mismatch,
    metric_mismatch,
    negative_gains_missing,
    question_map_mismatch,
    study_gain_count_mismatch,
    synthesis_invalid,
    pending_remain,
    performance_not_eligible,
    profile_count_mismatch,
    quality_duplicate,
    quality_row_mismatch,
    register_count_mismatch,
    register_duplicate,
    register_status_unknown,
    rq6_strategy_mismatch,
    selected_result_reused,
    study_master_duplicate,
    study_master_row_mismatch,
)

KNOWN_STATUSES = {STATUS_ELIGIBLE, STATUS_INELIGIBLE, STATUS_PENDING}
REGISTER_KEY = ["Study ID", "Baseline Study Instance ID"]


def duplicate_key_count(frame: pd.DataFrame, cols: list[str]) -> int:
    if not set(cols).issubset(frame.columns):
        return -1
    return int(frame.duplicated(cols).sum())


def analysis_ready_validation(raw: dict[str, pd.DataFrame], ready: dict[str, pd.DataFrame]) -> dict:
    master = ready["study_master"]
    register = ready["comparison_register"]
    performance = ready["performance_results"]
    audit = ready["performance_linkage_audit"]
    quality = ready["evidence_quality"]
    eligible = register[register["Status"].eq(STATUS_ELIGIBLE)]
    signed = pd.to_numeric(eligible["Signed Gain (pp)"], errors="coerce")
    calculated = pd.to_numeric(eligible["Mitigation (%)"], errors="coerce") - pd.to_numeric(eligible["Baseline (%)"], errors="coerce")
    gain_gaps = int((signed - calculated).abs().gt(1e-6).fillna(True).sum())
    withheld = register[register["Status"].ne(STATUS_ELIGIBLE)]
    if withheld["Signed Gain (pp)"].notna().any():
        gain_gaps += int(withheld["Signed Gain (pp)"].notna().sum())
    checks = {
        "raw_identification_rows": int(len(raw["identification"])),
        "unique_studies": int(master["Study ID"].nunique()),
        "study_master_rows": int(len(master)),
        "barrier_rows": int(len(raw["barriers"])),
        "mitigation_rows": int(len(raw["mitigations"])),
        "barrier_profile_rows": int(len(ready["barrier_profile"])),
        "mitigation_profile_rows": int(len(ready["mitigation_profile"])),
        "cooccurrence_rows": int(len(ready["barrier_mitigation_cooccurrence"])),
        "baseline_rows": int(len(raw["baselines"])),
        "register_rows": int(len(register)),
        "eligible_rows": int(register["Status"].eq(STATUS_ELIGIBLE).sum()),
        "ineligible_rows": int(register["Status"].eq(STATUS_INELIGIBLE).sum()),
        "pending_rows": int(register["Status"].eq(STATUS_PENDING).sum()),
        "mitigation_result_rows": int(len(raw["mitigation_results"])),
        "audit_rows": int(len(audit)),
        "performance_rows": int(len(performance)),
        "quality_rows": int(len(quality)),
        "duplicate_study_ids_master": duplicate_key_count(master, ["Study ID"]),
        "duplicate_quality_study_ids": duplicate_key_count(quality, ["Study ID"]),
        "duplicate_baseline_contexts": duplicate_key_count(register, REGISTER_KEY),
        "gain_mismatches": gain_gaps,
    }
    failures = []
    if checks["study_master_rows"] != checks["raw_identification_rows"] or checks["unique_studies"] != checks["raw_identification_rows"]:
        failures.append(study_master_row_mismatch())
    if checks["duplicate_study_ids_master"] != 0:
        failures.append(study_master_duplicate())
    if checks["quality_rows"] != checks["raw_identification_rows"]:
        failures.append(quality_row_mismatch())
    if checks["duplicate_quality_study_ids"] != 0:
        failures.append(quality_duplicate())
    if checks["barrier_profile_rows"] != checks["barrier_rows"] or checks["mitigation_profile_rows"] != checks["mitigation_rows"]:
        failures.append(profile_count_mismatch())
    if checks["register_rows"] != checks["baseline_rows"]:
        failures.append(register_count_mismatch())
    if checks["duplicate_baseline_contexts"] != 0:
        failures.append(register_duplicate())
    if checks["pending_rows"] != 0:
        failures.append(pending_remain())
    if checks["gain_mismatches"] != 0:
        failures.append(gain_mismatch())
    if checks["audit_rows"] != checks["mitigation_result_rows"]:
        failures.append(audit_count_mismatch())
    if not set(register["Status"]).issubset(KNOWN_STATUSES):
        failures.append(register_status_unknown())
    if register.loc[register["Status"].eq(STATUS_ELIGIBLE), "Selected Source Result Row"].dropna().duplicated().any():
        failures.append(selected_result_reused())
    if set(performance["Comparison ID"]) != set(eligible["Comparison ID"]):
        failures.append(performance_not_eligible())
    return {
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
    }


def statistics_validation(frames: dict[str, pd.DataFrame], tables: dict[str, pd.DataFrame], cfg: dict, question_map: dict) -> dict:
    effects = tables["rq3_study_gains"]
    synthesis = tables["rq3_task_synthesis"]
    included = tables["rq6_included_papers"]
    excluded = tables["rq6_excluded_papers"]
    strategies = frames["mitigation_profile"].dropna(subset=["Mitigation Strategy"]).groupby("Study ID")["Mitigation Strategy"].nunique()
    included_counts = included["Study ID"].map(strategies)
    performance = frames["performance_results"]
    expected_metric = performance["Task"].map(cfg["analysis"]["primary_metrics"])
    bootstrap = cfg["bootstrap"]
    listed = [name for section in question_map.values() for name in section["statistical_tables"]]
    checks = {
        "study_level_rows": int(len(effects)),
        "performance_rows": int(len(frames["performance_results"])),
        "duplicate_study_effects": int(effects["Study ID"].duplicated().sum()),
        "negative_gains": int((effects["study_gain"] < 0).sum()),
        "synthesis_tasks": synthesis["Task"].tolist(),
        "meaningful_column_present": "Meaningful n" in synthesis.columns or "Meaningful %" in synthesis.columns,
        "rq6_included_studies": int(included["Study ID"].nunique()),
        "rq6_excluded_studies": int(excluded["Study ID"].nunique()),
        "rq6_several_strategy_included": int(included_counts.gt(1).sum()),
        "metric_mismatches": int((performance["Metric Family"].astype(str) != expected_metric.astype(str)).sum()),
        "bootstrap_statistic": bootstrap["statistic"],
        "bootstrap_interval": bootstrap["interval"],
        "unmapped_tables": sorted(set(tables) - set(listed)),
        "unknown_mapped_tables": sorted(set(listed) - set(tables)),
        "repeated_mapped_tables": sorted({name for name in listed if listed.count(name) > 1}),
    }
    failures = []
    if checks["study_level_rows"] != checks["performance_rows"] or checks["duplicate_study_effects"] != 0:
        failures.append(study_gain_count_mismatch())
    if checks["negative_gains"] == 0:
        failures.append(negative_gains_missing())
    if checks["meaningful_column_present"] or checks["synthesis_tasks"] != list(cfg["analysis"]["task_order"]):
        failures.append(synthesis_invalid())
    if checks["rq6_several_strategy_included"] != 0:
        failures.append(rq6_strategy_mismatch())
    if checks["rq6_included_studies"] + checks["rq6_excluded_studies"] != checks["study_level_rows"]:
        failures.append(rq6_strategy_mismatch())
    if checks["metric_mismatches"] != 0:
        failures.append(metric_mismatch())
    if checks["bootstrap_statistic"] != "median" or checks["bootstrap_interval"] != "percentile":
        failures.append(bootstrap_setting_unsupported())
    if checks["unmapped_tables"] or checks["unknown_mapped_tables"] or checks["repeated_mapped_tables"]:
        failures.append(question_map_mismatch())
    return {
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
    }


def figures_validation(fig_cfg: dict, question_map: dict, figures_dir) -> dict:
    configured = list(fig_cfg["figures"])
    mapped = [name for section in question_map.values() for name in section.get("figures", [])]
    formats = {name: spec for name, spec in fig_cfg["output"]["formats"].items() if spec.get("enabled")}
    missing = []
    for key in configured:
        filename = fig_cfg["figures"][key].get("filename", key)
        for format_name, spec in formats.items():
            extension = "tiff" if format_name == "tiff" else format_name
            path = figures_dir / spec.get("folder", format_name) / f"{filename}.{extension}"
            if not path.exists():
                missing.append(path.name)
    checks = {
        "configured_figures": configured,
        "mapped_figures": mapped,
        "missing_files": missing,
        "map_without_config": sorted(set(mapped) - set(configured)),
    }
    failures = []
    if missing:
        failures.append(figure_missing())
    if checks["map_without_config"]:
        failures.append(figure_map_mismatch())
    return {
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
    }
