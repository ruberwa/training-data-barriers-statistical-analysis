import numpy as np
import pandas as pd
from scipy import stats


def percentile_interval(values, level=0.95):
    alpha = (1 - level) / 2
    return tuple(np.quantile(values, [alpha, 1 - alpha]))


def bootstrap_stat(values, statistic=np.median, repetitions=10000, seed=0, level=0.95):
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return np.nan, np.nan, np.array([])
    rng = np.random.default_rng(seed)
    draws = np.empty(repetitions)
    for i in range(repetitions):
        draws[i] = statistic(rng.choice(x, size=len(x), replace=True))
    low, high = percentile_interval(draws, level)
    return float(low), float(high), draws


def study_level_effects(performance):
    frame = performance.copy()
    frame["study_gain"] = pd.to_numeric(frame["Signed Gain (pp)"], errors="coerce")
    frame["study_baseline"] = pd.to_numeric(frame["Baseline (%)"], errors="coerce")
    return frame[["Task", "Study ID", "study_gain", "study_baseline"]].drop_duplicates(["Task", "Study ID"])


def synthesis_summary(study_effects, repetitions, seed, level=0.95, task_order=None):
    tasks = list(task_order) if task_order else list(study_effects["Task"].dropna().unique())
    rows = []
    for offset, task in enumerate(tasks):
        values = study_effects.loc[study_effects["Task"].eq(task), "study_gain"].dropna().to_numpy(float)
        if not len(values):
            rows.append({
                "Task": task, "Studies": 0, "Median gain (pp)": np.nan,
                "Bootstrap CI low": np.nan, "Bootstrap CI high": np.nan,
                "Q1": np.nan, "Q3": np.nan, "Minimum": np.nan, "Maximum": np.nan,
                "Positive n": 0, "Positive %": np.nan,
            })
            continue
        low, high, _ = bootstrap_stat(values, repetitions=repetitions, seed=seed + offset, level=level)
        rows.append({
            "Task": task, "Studies": len(values), "Median gain (pp)": float(np.median(values)),
            "Bootstrap CI low": low, "Bootstrap CI high": high,
            "Q1": float(np.quantile(values, 0.25)), "Q3": float(np.quantile(values, 0.75)),
            "Minimum": float(np.min(values)), "Maximum": float(np.max(values)),
            "Positive n": int((values > 0).sum()), "Positive %": 100 * float(np.mean(values > 0)),
        })
    return pd.DataFrame(rows)


def cramers_v(table):
    array = np.asarray(table, dtype=float)
    if array.size == 0 or array.sum() == 0 or min(array.shape) < 2:
        return np.nan
    chi2 = stats.chi2_contingency(array, correction=False)[0]
    n = array.sum()
    return float(np.sqrt((chi2 / n) / min(array.shape[0] - 1, array.shape[1] - 1)))


def multilabel_task_stat(tasks, incidence):
    task_values = np.asarray(tasks)
    matrix = np.asarray(incidence, dtype=int)
    levels = np.unique(task_values)
    total = 0.0
    for j in range(matrix.shape[1]):
        positive = np.array([matrix[task_values == level, j].sum() for level in levels], dtype=float)
        totals = np.array([(task_values == level).sum() for level in levels], dtype=float)
        table = np.column_stack([totals - positive, positive])
        if (table.sum(axis=0) > 0).all():
            total += stats.chi2_contingency(table, correction=False)[0]
    return float(total)


def permutation_task_multilabel(tasks, incidence, repetitions=10000, seed=0):
    observed = multilabel_task_stat(tasks, incidence)
    rng = np.random.default_rng(seed)
    exceed = 0
    original = np.asarray(tasks)
    for _ in range(repetitions):
        exceed += multilabel_task_stat(rng.permutation(original), incidence) >= observed - 1e-12
    return observed, (exceed + 1) / (repetitions + 1), exceed


def profile_association_stat(a, b):
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    observed = aa.T @ bb
    expected = np.outer(aa.sum(axis=0), bb.sum(axis=0)) / aa.shape[0]
    return float(np.sum((observed - expected) ** 2 / np.where(expected > 0, expected, 1)))


def permutation_profile_association(a, b, repetitions=10000, seed=0):
    observed = profile_association_stat(a, b)
    rng = np.random.default_rng(seed)
    exceed = 0
    b_array = np.asarray(b)
    for _ in range(repetitions):
        exceed += profile_association_stat(a, b_array[rng.permutation(len(b_array))]) >= observed - 1e-12
    return observed, (exceed + 1) / (repetitions + 1), exceed


def bootstrap_slope(frame, x, y, repetitions, seed, level=0.95):
    clean = frame[[x, y]].dropna()
    if len(clean) < 3 or clean[x].nunique() < 2:
        return np.nan, np.nan, np.array([])
    rng = np.random.default_rng(seed)
    slopes = []
    for _ in range(repetitions):
        sample = clean.iloc[rng.integers(0, len(clean), len(clean))]
        if sample[x].nunique() >= 2:
            slopes.append(stats.linregress(sample[x], sample[y]).slope)
    low, high = percentile_interval(slopes, level)
    return float(low), float(high), np.asarray(slopes)


def permutation_slope_p(frame, x, y, repetitions, seed):
    clean = frame[[x, y]].dropna()
    if len(clean) < 3 or clean[x].nunique() < 2:
        return np.nan
    observed = stats.linregress(clean[x], clean[y]).slope
    rng = np.random.default_rng(seed)
    exceed = 0
    yy = clean[y].to_numpy()
    xx = clean[x].to_numpy()
    for _ in range(repetitions):
        exceed += abs(stats.linregress(xx, rng.permutation(yy)).slope) >= abs(observed) - 1e-12
    return (exceed + 1) / (repetitions + 1)
