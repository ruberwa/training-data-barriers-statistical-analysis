from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from utils.statistics import (
    bootstrap_slope,
    bootstrap_stat,
    cramers_v,
    percentile_interval,
    permutation_profile_association,
    permutation_slope_p,
    permutation_task_multilabel,
    study_level_effects,
    synthesis_summary,
)


def _bootstrap(cfg):
    block = cfg["bootstrap"]
    return int(block["seed"]), int(block["repetitions"]), int(block["permutation_repetitions"]), float(block["level"])


def _nunique_pairs(frame, columns):
    return frame[columns].dropna().drop_duplicates()


def _prevalence(frame, column, denominator):
    counts = frame[column].dropna().value_counts()
    out = counts.rename("Records").reset_index()
    studies = frame.dropna(subset=[column]).groupby(column)["Study ID"].nunique()
    out["Studies"] = out[column].map(studies)
    out["Study prevalence %"] = 100 * out["Studies"] / denominator
    return out


def _task_prevalence(frame, column):
    rows = []
    for task, group in frame.dropna(subset=[column]).groupby("Task"):
        studies = group.groupby(column)["Study ID"].nunique()
        task_n = group["Study ID"].nunique()
        for level, count in studies.items():
            rows.append({"Task": task, column: level, "Studies": int(count), "Task studies": int(task_n), "Percent": 100 * count / task_n})
    return pd.DataFrame(rows)


def _cooccurrence(frame, column):
    pairs = frame.dropna(subset=[column]).groupby("Study ID")[column].apply(lambda s: sorted(set(s)))
    rows = {}
    for values in pairs:
        for i, left in enumerate(values):
            for right in values[i + 1:]:
                key = (left, right)
                rows[key] = rows.get(key, 0) + 1
    return pd.DataFrame([{"First": a, "Second": b, "Studies": n} for (a, b), n in sorted(rows.items())])


def _country_rows(master):
    rows = []
    for _, row in master.iterrows():
        text = str(row.get("Country", "")).strip()
        if not text or text.lower() == "nan":
            continue
        for country in [part.strip() for part in text.split(";") if part.strip()]:
            rows.append({"Study ID": row["Study ID"], "Country": country})
    return pd.DataFrame(rows)


def descriptive_tables(frames, cfg):
    master = frames["study_master"].copy()
    barriers = frames["barrier_profile"]
    mitigations = frames["mitigation_profile"]
    performance = frames["performance_results"]
    studies = master["Study ID"].nunique()
    task_order = cfg["analysis"]["task_order"]
    years = master.dropna(subset=["Year"]).groupby("Year")["Study ID"].nunique().rename("Studies").reset_index()
    tasks = master["Task"].value_counts().reindex(task_order).fillna(0).astype(int).rename("Studies").reset_index()
    environments = master["Environment"].fillna("Not reported").value_counts().rename("Studies").reset_index()
    countries = _country_rows(master)
    country_counts = countries["Country"].value_counts().rename("Studies").reset_index() if len(countries) else pd.DataFrame(columns=["Country", "Studies"])
    size = pd.to_numeric(master["Dataset Size (numeric)"], errors="coerce")
    size_rows = []
    for task in task_order:
        values = size[master["Task"].eq(task)].dropna()
        size_rows.append({
            "Task": task,
            "Studies with a clear size": int(values.shape[0]),
            "Median": float(values.median()) if len(values) else np.nan,
            "Minimum": float(values.min()) if len(values) else np.nan,
            "Maximum": float(values.max()) if len(values) else np.nan,
        })
    metrics = performance.groupby(["Task", "Metric Family"])["Study ID"].nunique().rename("Studies").reset_index()
    return {
        "evidence_publication_year": years,
        "evidence_task": tasks,
        "evidence_environment": environments,
        "evidence_country": country_counts,
        "evidence_dataset_size": pd.DataFrame(size_rows),
        "evidence_metric": metrics,
        "rq1_barrier_category": _prevalence(barriers, "Barrier Category", studies),
        "rq1_barrier_type": _prevalence(barriers, "Normalized Barrier", studies),
        "rq1_barrier_by_task": _task_prevalence(barriers, "Barrier Category"),
        "rq1_barrier_cooccurrence": _cooccurrence(barriers, "Normalized Barrier"),
        "rq2_mitigation_category": _prevalence(mitigations, "Mitigation Category", studies),
        "rq2_mitigation_strategy": _prevalence(mitigations, "Mitigation Strategy", studies),
        "rq2_mitigation_by_task": _task_prevalence(mitigations, "Mitigation Strategy"),
    }


def rq1_rq2_associations(frames, cfg):
    master = frames["study_master"]
    barriers = frames["barrier_profile"]
    mitigations = frames["mitigation_profile"]
    cooccurrence = frames["barrier_mitigation_cooccurrence"]
    seed, _, reps, _ = _bootstrap(cfg)
    barrier_pairs = _nunique_pairs(barriers, ["Study ID", "Barrier Category"])
    barrier_inc = pd.crosstab(barrier_pairs["Study ID"], barrier_pairs["Barrier Category"]).clip(upper=1)
    h1_base = master[["Study ID", "Task"]].drop_duplicates().set_index("Study ID").join(barrier_inc, how="inner")
    barrier_cols = [column for column in h1_base.columns if column != "Task"]
    observed1, p1, exceed1 = permutation_task_multilabel(h1_base["Task"].to_numpy(), h1_base[barrier_cols].to_numpy(), repetitions=reps, seed=seed)
    h1_counts = pd.crosstab(barriers.dropna(subset=["Barrier Category"])["Task"], barriers.dropna(subset=["Barrier Category"])["Barrier Category"])
    h1 = pd.DataFrame([{
        "Test": "Task x barrier multi-label study-preserving permutation",
        "Statistic": observed1, "Permutation p": p1, "Permutation exceedances": exceed1,
        "Repetitions": reps, "Descriptive Cramer's V": cramers_v(h1_counts), "Studies": len(h1_base),
    }])
    barrier_profile = _nunique_pairs(barriers, ["Study ID", "Barrier Category"])
    mitigation_profile = _nunique_pairs(mitigations, ["Study ID", "Mitigation Category"])
    barrier_matrix = pd.crosstab(barrier_profile["Study ID"], barrier_profile["Barrier Category"]).clip(upper=1)
    mitigation_matrix = pd.crosstab(mitigation_profile["Study ID"], mitigation_profile["Mitigation Category"]).clip(upper=1)
    shared = barrier_matrix.index.intersection(mitigation_matrix.index)
    observed2, p2, exceed2 = permutation_profile_association(barrier_matrix.loc[shared].to_numpy(), mitigation_matrix.loc[shared].to_numpy(), repetitions=reps, seed=seed + 1)
    paper_pairs = barrier_profile.merge(mitigation_profile, on="Study ID", how="inner")
    pair_counts = pd.crosstab(paper_pairs["Barrier Category"], paper_pairs["Mitigation Category"])
    h2 = pd.DataFrame([{
        "Test": "Barrier x mitigation study-profile permutation",
        "Count rule": "Same paper",
        "Statistic": observed2, "Permutation p": p2, "Permutation exceedances": exceed2,
        "Repetitions": reps, "Descriptive Cramer's V": cramers_v(pair_counts), "Studies": len(shared),
    }])
    row_pct = pair_counts.div(pair_counts.sum(axis=1).replace(0, np.nan), axis=0) * 100
    same_instance = cooccurrence[cooccurrence["Co-occurrence"].eq("Same-instance co-occurrence")]
    same_counts = pd.crosstab(same_instance["Barrier Category"], same_instance["Mitigation Category"]) if len(same_instance) else pd.DataFrame()
    return {
        "rq1_task_barrier_test": h1,
        "rq1_task_barrier_counts": h1_counts.reset_index(),
        "rq2_profile_test": h2,
        "rq2_same_paper_counts": pair_counts.reset_index(),
        "rq2_same_paper_percent": row_pct.reset_index(),
        "rq2_same_instance": same_counts.reset_index() if len(same_counts) else pd.DataFrame(columns=["Barrier Category"]),
    }


def rq3_performance(frames, cfg):
    study = study_level_effects(frames["performance_results"])
    seed, reps, _, level = _bootstrap(cfg)
    summary = synthesis_summary(
        study,
        reps,
        seed,
        level=level,
        task_order=cfg["analysis"]["task_order"],
    )
    return {
        "rq3_study_gains": study,
        "rq3_task_synthesis": summary,
    }


def _task_regression(study, variable, cfg):
    tasks = cfg["analysis"]["task_order"]
    seed, reps, preps, level = _bootstrap(cfg)
    min_n = int(cfg["analysis"]["minimum_regression_studies"])
    rows = []
    for index, task in enumerate(tasks):
        data = study[study["Task"].eq(task)][[variable, "study_gain"]].dropna().copy()
        if len(data) < min_n or data[variable].nunique() < 2:
            rows.append({"Task": task, "Moderator": variable, "Studies": len(data), "Slope": np.nan, "CI low": np.nan, "CI high": np.nan, "Permutation p": np.nan, "Pearson r": np.nan})
            continue
        fit = stats.linregress(data[variable], data["study_gain"])
        low, high, _ = bootstrap_slope(data, variable, "study_gain", reps, seed + index, level)
        p_value = permutation_slope_p(data, variable, "study_gain", preps, seed + 100 + index)
        rows.append({"Task": task, "Moderator": variable, "Studies": len(data), "Slope": fit.slope, "CI low": low, "CI high": high, "Permutation p": p_value, "Pearson r": fit.rvalue})
    return pd.DataFrame(rows)


def _group_summary(study_rows, group_col, min_n):
    rows = []
    for (task, level), group in study_rows.dropna(subset=[group_col]).groupby(["Task", group_col]):
        values = group["study_gain"].dropna().to_numpy(float)
        if len(values) >= min_n:
            rows.append({"Task": task, group_col: level, "Studies": len(values), "Median gain (pp)": float(np.median(values)), "Q1": float(np.quantile(values, 0.25)), "Q3": float(np.quantile(values, 0.75))})
    return pd.DataFrame(rows)


def rq4_moderators(frames, cfg):
    master = frames["study_master"]
    min_n = int(cfg["analysis"]["minimum_subgroup_studies"])
    study = study_level_effects(frames["performance_results"])
    study = study.merge(master[["Study ID", "Environment", "Dataset Size (numeric)"]], on="Study ID", how="left", validate="one_to_one")
    baseline = _task_regression(study, "study_baseline", cfg)
    dataset = study.copy()
    dataset["log_dataset_size"] = np.log10(pd.to_numeric(dataset["Dataset Size (numeric)"], errors="coerce").where(lambda values: values > 0))
    continuous = pd.concat([baseline, _task_regression(dataset, "log_dataset_size", cfg)], ignore_index=True)
    strategies = frames["mitigation_profile"][["Study ID", "Mitigation Strategy"]].dropna().drop_duplicates()
    barriers = frames["barrier_profile"][["Study ID", "Normalized Barrier"]].dropna().drop_duplicates()
    return {
        "rq4_baseline_and_size": continuous,
        "rq4_environment": _group_summary(study[["Task", "Study ID", "Environment", "study_gain"]], "Environment", min_n),
        "rq4_mitigation": _group_summary(study.merge(strategies, on="Study ID", how="inner"), "Mitigation Strategy", min_n),
        "rq4_barrier": _group_summary(study.merge(barriers, on="Study ID", how="inner"), "Normalized Barrier", min_n),
    }


def _quality_join(study_effects, quality):
    columns = ["Study ID", "Independent Test Set", "Data Leakage Prevented", "Appropriate Metrics", "Related Samples Separated", "Overall Risk of Bias"]
    return study_effects.merge(quality[columns], on="Study ID", how="left", validate="one_to_one")


def rq5_credibility(frames, cfg):
    quality = frames["evidence_quality"].copy()
    seed, reps, _, level = _bootstrap(cfg)
    task_order = cfg["analysis"]["task_order"]
    low_extreme = float(cfg["analysis"]["extreme_gain_lower_pp"])
    high_extreme = float(cfg["analysis"]["extreme_gain_upper_pp"])
    study = study_level_effects(frames["performance_results"])
    joined = _quality_join(study, quality)
    rows = []
    for index, scenario in enumerate(cfg.get("sensitivity_scenarios", [])):
        if scenario == "mean_within_study":
            continue
        subset = joined
        if scenario == "exclude_high_risk":
            subset = joined[~joined["Overall Risk of Bias"].astype(str).str.lower().eq("high")]
        elif scenario == "independent_test_set_only":
            subset = joined[joined["Independent Test Set"].eq("Yes")]
        elif scenario == "leakage_prevented_only":
            subset = joined[joined["Data Leakage Prevented"].eq("Yes")]
        elif scenario == "related_samples_separated_only":
            subset = joined[joined["Related Samples Separated"].eq("Yes")]
        elif scenario == "all_credibility_criteria_met":
            subset = joined[joined["Independent Test Set"].eq("Yes") & joined["Data Leakage Prevented"].eq("Yes") & joined["Related Samples Separated"].eq("Yes") & joined["Appropriate Metrics"].eq("Yes")]
        elif scenario == "exclude_extreme_gains":
            subset = joined[joined["study_gain"].between(low_extreme, high_extreme)]
        summary = synthesis_summary(subset[["Task", "Study ID", "study_gain"]], reps, seed + index * 10, level=level, task_order=task_order)
        summary.insert(0, "Scenario", scenario)
        rows.append(summary)
    criteria = [column for column in quality.columns if column not in {"Study ID", "Title", "Task"}]
    quality_rows = []
    for criterion in criteria:
        for judgment, count in quality[criterion].fillna("Not reported").value_counts().items():
            quality_rows.append({"Criterion": criterion, "Judgment": judgment, "Studies": int(count), "Percent": 100 * count / len(quality)})
    loo_rows = []
    for task, group in study.groupby("Task"):
        full = float(group["study_gain"].median())
        for study_id in group["Study ID"]:
            remaining = group[group["Study ID"] != study_id]["study_gain"]
            median = float(remaining.median()) if len(remaining) else np.nan
            loo_rows.append({"Task": task, "Excluded Study ID": study_id, "Full median": full, "LOO median": median, "Change": median - full})
    return {
        "rq5_quality": pd.DataFrame(quality_rows),
        "rq5_sensitivity": pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(),
        "rq5_leave_one_paper_out": pd.DataFrame(loo_rows),
    }


def _ols_synthetic_coefficient(frame):
    data = frame.dropna(subset=["study_gain", "study_baseline", "Synthetic Family", "Task"]).copy()
    if data.empty or data["Synthetic Family"].nunique() < 2:
        return np.nan
    synthetic = (data["Synthetic Family"] == "Synthetic Image Methods").astype(float).to_numpy()
    baseline = data["study_baseline"].astype(float).to_numpy()
    task_dummies = pd.get_dummies(data["Task"], drop_first=True, dtype=float)
    columns = [np.ones(len(data)), synthetic, baseline]
    for column in task_dummies.columns:
        columns.append(task_dummies[column].to_numpy())
    matrix = np.column_stack(columns)
    outcome = data["study_gain"].astype(float).to_numpy()
    if np.linalg.matrix_rank(matrix) < matrix.shape[1]:
        return np.nan
    return float(np.linalg.lstsq(matrix, outcome, rcond=None)[0][1])


def rq6_synthetic(frames, cfg):
    study = study_level_effects(frames["performance_results"])
    profile = frames["mitigation_profile"].dropna(subset=["Mitigation Strategy"]).copy()
    counts = profile.groupby("Study ID")["Mitigation Strategy"].nunique()
    single_ids = counts[counts.eq(1)].index
    single = profile[profile["Study ID"].isin(single_ids)].drop_duplicates("Study ID")
    excluded_ids = study.loc[~study["Study ID"].isin(single_ids), "Study ID"]
    excluded = pd.DataFrame({
        "Study ID": excluded_ids.to_numpy(),
        "Reason": np.where(excluded_ids.map(counts).fillna(0).gt(1), "Several mitigation strategies", "No mitigation strategy"),
    })
    joined = study.merge(single[["Study ID", "Mitigation Strategy", "Synthetic Image Method", "Synthetic Type"]], on="Study ID", how="inner")
    joined["Synthetic Family"] = np.where(joined["Synthetic Image Method"].eq("Yes"), "Synthetic Image Methods", "Other Mitigation Methods")
    seed, reps, _, level = _bootstrap(cfg)
    raw_rows = []
    for index, ((task, family), group) in enumerate(joined.groupby(["Task", "Synthetic Family"])):
        values = group["study_gain"].dropna().to_numpy(float)
        low, high, _ = bootstrap_stat(values, repetitions=reps, seed=seed + index, level=level)
        raw_rows.append({"Task": task, "Method Family": family, "Studies": len(values), "Median gain (pp)": float(np.median(values)) if len(values) else np.nan, "CI low": low, "CI high": high})
    coefficient = _ols_synthetic_coefficient(joined)
    rng = np.random.default_rng(seed + 600)
    studies = joined["Study ID"].unique()
    draws = []
    if len(studies) >= 5 and np.isfinite(coefficient):
        grouped = {study_id: joined[joined["Study ID"].eq(study_id)] for study_id in studies}
        for _ in range(reps):
            sampled = rng.choice(studies, size=len(studies), replace=True)
            estimate = _ols_synthetic_coefficient(pd.concat([grouped[study_id] for study_id in sampled], ignore_index=True))
            if np.isfinite(estimate):
                draws.append(estimate)
    if draws:
        ci_low, ci_high = percentile_interval(draws, level)
        p_boot = 2 * min(np.mean(np.asarray(draws) <= 0), np.mean(np.asarray(draws) >= 0))
    else:
        ci_low = ci_high = p_boot = np.nan
    subtype_rows = []
    subtype = joined[joined["Synthetic Image Method"].eq("Yes")]
    for (task, synthetic_type), group in subtype.groupby(["Task", "Synthetic Type"]):
        values = group["study_gain"].dropna().to_numpy(float)
        subtype_rows.append({"Task": task, "Synthetic Type": synthetic_type, "Studies": len(values), "Median gain (pp)": float(np.median(values)) if len(values) else np.nan})
    return {
        "rq6_included_papers": joined,
        "rq6_excluded_papers": excluded,
        "rq6_method_summary": pd.DataFrame(raw_rows),
        "rq6_adjusted_contrast": pd.DataFrame([{
            "Comparison": "Synthetic Image Methods vs Other Mitigation Methods",
            "Adjusted difference (pp)": coefficient,
            "Bootstrap CI low": ci_low,
            "Bootstrap CI high": ci_high,
            "Bootstrap two-sided p": p_boot,
            "Independent studies": len(studies),
            "Adjustment": "Baseline performance + task",
            "Entry rule": "One mitigation strategy",
        }]),
        "rq6_synthetic_subtypes": pd.DataFrame(subtype_rows),
    }


def run_all_statistics(frames, cfg):
    tables = {}
    for function in (descriptive_tables, rq1_rq2_associations, rq3_performance, rq4_moderators, rq5_credibility, rq6_synthetic):
        bundle = function(frames, cfg)
        overlap = set(tables).intersection(bundle)
        if overlap:
            raise RuntimeError(f"Duplicate statistical output names: {sorted(overlap)}")
        tables.update(bundle)
    return tables
