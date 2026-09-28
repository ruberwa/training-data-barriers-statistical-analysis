from __future__ import annotations

import colorsys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pycountry
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

from common.Messages import map_not_found, unmatched_countries
from common.paths import MAP_FILE
from utils.plotting import figure_size, save_figure


def _read(directory: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(directory / f"{name}.csv")


def _tasks(analysis_cfg: dict) -> list[str]:
    return list(analysis_cfg["analysis"]["task_order"])


def _task_color(fig_cfg: dict, task: str) -> str:
    return fig_cfg["palette"]["tasks"].get(task, "#355C7D")


def _minimum(fig_cfg: dict, key: str | None = None) -> int:
    display = _shared(fig_cfg, key, "display") if key else fig_cfg.get("display", {})
    return int(display.get("minimum_studies", 5))


def _spec(fig_cfg: dict, key: str) -> dict:
    return fig_cfg["figures"][key]


def _shared(fig_cfg: dict, key: str, name: str) -> dict:
    spec = fig_cfg["figures"].get(key, {})
    if name in spec:
        return spec[name]
    return fig_cfg.get(name, {})


def _table(fig_cfg: dict, key: str, name: str) -> str:
    return _spec(fig_cfg, key)["tables"][name]


def _panel_cfg(fig_cfg: dict, key: str, letter: str) -> dict:
    return _spec(fig_cfg, key).get("panels", {}).get(letter, {})


def _bound(fig_cfg: dict, key: str) -> dict:
    bound = dict(fig_cfg)
    spec = fig_cfg["figures"][key]
    for name in ("output", "display", "geography", "publication", "theme", "palette", "card", "grid", "donut"):
        if name in spec:
            bound[name] = spec[name]
    return bound


def _panel(ax, label: str, y: float = 1.04) -> None:
    ax.text(-0.02, y, label, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom", ha="right")


def _style(ax, grid_axis: str = "y") -> None:
    ax.grid(True, axis=grid_axis, color="#E3E3E3", linewidth=0.6)
    ax.set_axisbelow(True)


def _forest(ax, x, low, high, y, color, marker="o", ms=4.5) -> None:
    ax.errorbar(x, y, xerr=[[max(x - low, 0)], [max(high - x, 0)]], fmt=marker, color=color, ecolor=color, ms=ms, lw=1.1, capsize=2)


def _regression(x, y, grid):
    if len(x) < 2 or np.unique(x).size < 2:
        return None, None, None
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    residual = np.sqrt(np.sum((y - fitted) ** 2) / max(len(x) - 2, 1))
    denom = np.sum((x - x.mean()) ** 2)
    line = intercept + slope * grid
    if denom <= 0:
        return line, None, None
    band = 1.96 * residual * np.sqrt(1 / len(x) + (grid - x.mean()) ** 2 / denom)
    return line, line - band, line + band


def _iso3(country: str):
    name = str(country).strip()
    aliases = {
        "USA": "USA",
        "United States": "USA",
        "United States of America": "USA",
        "Czech Republic": "CZE",
        "Czechia": "CZE",
        "South Korea": "KOR",
        "Korea, South": "KOR",
        "Türkiye": "TUR",
        "Turkey": "TUR",
        "UK": "GBR",
        "United Kingdom": "GBR",
    }
    if not name or name.lower() in {"nan", "not reported", "none"}:
        return None
    if name in aliases:
        return aliases[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None


def _display_country(iso3: str) -> str:
    custom = {"USA": "United States of America", "GBR": "United Kingdom", "KOR": "Korea, Republic of"}
    if iso3 in custom:
        return custom[iso3]
    country = pycountry.countries.get(alpha_3=iso3)
    return country.name if country is not None else iso3


def _rose_or_pink(color) -> bool:
    red, green, blue = color[:3]
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    if saturation < 0.15:
        return False
    if 0.78 <= hue <= 0.98:
        return True
    return (hue <= 0.05 or hue >= 0.96) and value >= 0.82 and saturation <= 0.72


def _country_colors(count: int) -> list:
    cmaps = [plt.cm.tab20, plt.cm.tab20b, plt.cm.tab20c, plt.cm.Set3, plt.cm.Paired]
    colors = []
    for cmap in cmaps:
        size = getattr(cmap, "N", 12)
        for index in range(size):
            color = cmap(index / max(size - 1, 1))
            if _rose_or_pink(color):
                continue
            colors.append(color)
            if len(colors) >= count:
                return colors
    return colors[:count]


def evidence_study_profile(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    fig_cfg = _bound(fig_cfg, "evidence_study_profile")
    master = _read(ready_dir, _table(fig_cfg, "evidence_study_profile", "master"))
    master["Year"] = pd.to_numeric(master["Year"], errors="coerce")
    master["Dataset Size (numeric)"] = pd.to_numeric(master["Dataset Size (numeric)"], errors="coerce")
    tasks = _tasks(analysis_cfg)
    counts = master.dropna(subset=["Year"]).groupby(["Year", "Task"])["Study ID"].nunique().unstack(fill_value=0).reindex(columns=tasks, fill_value=0).sort_index()
    fig = plt.figure(figsize=figure_size(fig_cfg, "evidence_study_profile"))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.28)
    year_ax = fig.add_subplot(grid[0, 0])
    size_ax = fig.add_subplot(grid[0, 1])
    x = np.arange(len(counts))
    bottoms = np.zeros(len(counts))
    study_total = master["Study ID"].nunique()
    for task in tasks:
        values = counts[task].to_numpy(float)
        task_count = int(master.loc[master["Task"].eq(task), "Study ID"].nunique())
        task_share = 100 * task_count / study_total if study_total else 0
        year_ax.bar(x, values, bottom=bottoms, color=_task_color(fig_cfg, task), label=f"{task}: {task_count} ({task_share:.1f}%)", width=0.72)
        bottoms = bottoms + values
    total_studies = float(bottoms.sum()) if len(bottoms) else 0
    for index, total in enumerate(bottoms):
        share = 100 * total / total_studies if total_studies else 0
        year_ax.text(x[index], total + max(bottoms) * 0.03, f"{int(total)} ({share:.1f}%)", ha="center", va="bottom", fontsize=6.5)
    year_ax.set_ylim(0, max(bottoms) * 1.18 if len(bottoms) else 1)
    year_ax.set_xticks(x)
    year_ax.set_xticklabels(counts.index.astype(int).astype(str))
    year_panel = _panel_cfg(fig_cfg, "evidence_study_profile", "A")
    year_ax.set_ylabel(year_panel.get("ylabel", "Number of studies"))
    year_ax.set_xlabel(year_panel.get("xlabel", "Publication year"))
    _panel(year_ax, year_panel.get("letter", "A"), 0.98)
    _style(year_ax)
    year_ax.legend(frameon=False, loc="upper left")
    valid = master.loc[master["Task"].isin(tasks) & master["Dataset Size (numeric)"].gt(0)]
    data = [valid.loc[valid["Task"].eq(task), "Dataset Size (numeric)"].dropna().to_numpy(float) for task in tasks]
    boxes = size_ax.boxplot([values for values in data if len(values)] or [np.array([np.nan])], tick_labels=[task for task, values in zip(tasks, data) if len(values)], patch_artist=True, widths=0.55, showfliers=False)
    shown = [task for task, values in zip(tasks, data) if len(values)]
    for patch, task in zip(boxes["boxes"], shown):
        patch.set_facecolor(_task_color(fig_cfg, task))
        patch.set_alpha(0.9)
        patch.set_edgecolor("black")
    for element in ("whiskers", "caps"):
        for line in boxes[element]:
            line.set_color("black")
    for line in boxes["medians"]:
        line.set_color("black")
        line.set_linewidth(1.2)
    size_ax.set_yscale("log")
    rng = np.random.default_rng(int(analysis_cfg.get("bootstrap", {}).get("seed", 20260903)))
    shown_values = [values for values in data if len(values)]
    for index, values in enumerate(shown_values, start=1):
        size_ax.scatter(rng.normal(index, 0.06, len(values)), values, s=8, color="#4D4D4D", alpha=0.45, edgecolors="none")
        task = shown[index - 1]
        task_count = int(master.loc[master["Task"].eq(task), "Study ID"].nunique())
        share = 100 * len(values) / task_count if task_count else 0
        size_ax.text(index, values.max() * 1.45, f"n = {len(values)} ({share:.1f}%)", ha="center", va="bottom", fontsize=7)
    low, _ = size_ax.get_ylim()
    highest = max(values.max() for values in shown_values)
    size_ax.set_ylim(low, highest * 3)
    size_panel = _panel_cfg(fig_cfg, "evidence_study_profile", "B")
    _panel(size_ax, size_panel.get("letter", "B"), 0.98)
    size_ax.set_ylabel(size_panel.get("ylabel", "Dataset size"))
    size_ax.set_xlabel(size_panel.get("xlabel", "Task"))
    _style(size_ax)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.14)
    return save_figure(fig, fig_cfg, "evidence_study_profile", fig_dir)


def evidence_geography(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    fig_cfg = _bound(fig_cfg, "evidence_geography")
    if not MAP_FILE.exists():
        raise FileNotFoundError(map_not_found(MAP_FILE))
    recorded = _read(stat_dir, _table(fig_cfg, "evidence_geography", "country"))
    parts = []
    for _, row in recorded.iterrows():
        for name in str(row["Country"]).split(","):
            cleaned = name.strip()
            if cleaned:
                parts.append({"Country": cleaned, "Studies": row["Studies"]})
    country = pd.DataFrame(parts)
    country["ISO3"] = country["Country"].map(_iso3)
    unmatched = sorted(country.loc[country["ISO3"].isna() & ~country["Country"].astype(str).str.lower().eq("not reported"), "Country"].astype(str).unique())
    counts = country.dropna(subset=["ISO3"]).groupby("ISO3", as_index=False)["Studies"].sum()
    master = _read(ready_dir, _table(fig_cfg, "evidence_geography", "master"))
    country_text = master["Country"].fillna("").astype(str).str.strip()
    not_reported = int(country_text.isin({"", "nan", "None", "none"}).sum())
    world = gpd.read_file(MAP_FILE)
    iso_column = "iso_a3" if "iso_a3" in world.columns else "ISO_A3"
    listed = counts.sort_values(["Studies", "ISO3"], ascending=[False, True]).reset_index(drop=True)
    palette = _country_colors(len(listed))
    color_map = dict(zip(listed["ISO3"], palette))
    geography = _shared(fig_cfg, "evidence_geography", "geography")
    world["fill_color"] = world[iso_column].map(color_map).fillna(geography["no_study_color"])
    fig = plt.figure(figsize=figure_size(fig_cfg, "evidence_geography"))
    grid = fig.add_gridspec(2, 1, height_ratios=[3.2, 1.8], hspace=0.02)
    map_ax = fig.add_subplot(grid[0])
    list_ax = fig.add_subplot(grid[1])
    world.plot(ax=map_ax, color=world["fill_color"], edgecolor=geography["border_color"], linewidth=geography["border_width"])
    map_ax.set_ylim(-58, 85)
    map_ax.set_axis_off()
    total = float(listed["Studies"].sum()) + not_reported
    rows = [(color_map[row["ISO3"]], f"{_display_country(row['ISO3'])}: {int(row['Studies'])} ({100 * row['Studies'] / total:.1f}%)") for _, row in listed.iterrows()]
    if not_reported:
        rows.append((geography.get("not_reported_color", "#B8BCC2"), f"Not reported: {not_reported} ({100 * not_reported / total:.1f}%)"))
    list_ax.axis("off")
    columns = 4 if len(rows) > 16 else 3
    row_count = int(np.ceil(len(rows) / columns)) if len(rows) else 1
    list_ax.set_xlim(0, columns)
    list_ax.set_ylim(0, row_count)
    for index, (color, label) in enumerate(rows):
        column = index // row_count
        row = index % row_count
        x0 = column + 0.04
        y0 = row_count - row - 0.7
        list_ax.add_patch(Rectangle((x0, y0), 0.08, 0.28, facecolor=color, edgecolor="none", transform=list_ax.transData))
        list_ax.text(x0 + 0.12, y0 + 0.14, label, va="center", ha="left", fontsize=6.2, color="#4D4D4D")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return save_figure(fig, fig_cfg, "evidence_geography", fig_dir), unmatched


def _item_category(frame: pd.DataFrame, item: str, category: str) -> pd.Series:
    pairs = frame.dropna(subset=[item, category]).drop_duplicates([item, category])
    return pairs.groupby(item)[category].agg(lambda values: values.mode().iloc[0])


def _ink(color) -> str:
    if isinstance(color, str):
        value = color.lstrip("#")
        channels = [int(value[index:index + 2], 16) for index in (0, 2, 4)]
    else:
        channels = [int(channel * 255) for channel in color[:3]]
    red, green, blue = channels
    luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
    return "#1A1A1A" if luminance > 0.62 else "white"


def _category_label(code: str) -> str:
    names = {"IMAGING": "Imaging", "ENVIRONMENTAL": "Environmental", "DATA": "Data", "TECHNICAL": "Technical"}
    return names.get(code, code)


def _ranked(frame: pd.DataFrame, item: str, fig_cfg: dict, key: str | None = None) -> pd.DataFrame:
    kept = frame.loc[frame["Studies"] >= _minimum(fig_cfg, key)].sort_values(["Studies", item], ascending=[True, False])
    return kept.reset_index(drop=True)


def _count_labels(ax, studies, percents, span: float) -> None:
    for y, count, percent in zip(range(len(studies)), studies, percents):
        ax.text(count + span * 0.015, y, f"{int(count)} ({percent:.1f}%)", va="center", ha="left", fontsize=6.5, color="#4D4D4D")


def _record_pie(ax, records: pd.DataFrame, category: str, palette: dict, fig_cfg: dict, key: str) -> None:
    donut = _shared(fig_cfg, key, "donut")
    order = [code for code in palette if code in set(records[category])]
    ordered = records.set_index(category).reindex(order).dropna(subset=["Records"])
    colors = [palette[code] for code in ordered.index]
    labels = [_category_label(str(code)) for code in ordered.index]
    pie_ax = ax.inset_axes([0.55, 0.16, 0.42, 0.40])
    pie_ax.set_zorder(4)
    pie_ax.set_facecolor("white")
    wedges, _, autotexts = pie_ax.pie(ordered["Records"], colors=colors, startangle=90, wedgeprops={"width": donut.get("width", 0.68), "edgecolor": "white", "linewidth": 0.6}, autopct=lambda share: f"{share:.1f}%", pctdistance=donut.get("pctdistance", 0.66), textprops={"fontsize": 6.5})
    pie_ax.add_artist(plt.Circle((0, 0), donut.get("hole", 0.32), facecolor="white", edgecolor="none", zorder=2))
    for wedge, text in zip(wedges, autotexts):
        text.set_color(_ink(wedge.get_facecolor()))
        text.set_zorder(3)
    pie_ax.legend(wedges, labels, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.04), fontsize=6, ncol=2, handlelength=0.8, columnspacing=0.6)


def _corner(ax, label: str) -> None:
    ax.text(0.0, 1.02, label, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom", ha="left", clip_on=False)


def _frame_panels(fig, groups, fig_cfg: dict, key: str) -> None:
    share = _spec(fig_cfg, key).get("card_share", "height")
    card = _shared(fig_cfg, key, "card")
    edge = card.get("edgecolor", "black")
    width = card.get("linewidth", 0.9)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    frames = []
    for group in groups:
        boxes = [item.get_tightbbox(renderer).transformed(fig.transFigure.inverted()) for item in group]
        frames.append((min(box.x0 for box in boxes) - 0.008, min(box.y0 for box in boxes) - 0.012, max(box.x1 for box in boxes) + 0.008, max(box.y1 for box in boxes) + 0.012))
    if share == "width":
        shared_left = min(frame[0] for frame in frames)
        shared_right = max(frame[2] for frame in frames)
        for _, bottom, _, top in frames:
            fig.add_artist(Rectangle((shared_left, bottom), shared_right - shared_left, top - bottom, transform=fig.transFigure, fill=False, linewidth=width, edgecolor=edge, zorder=5))
    else:
        shared_bottom = min(frame[1] for frame in frames)
        shared_top = max(frame[3] for frame in frames)
        for left, _, right, _ in frames:
            fig.add_artist(Rectangle((left, shared_bottom), right - left, shared_top - shared_bottom, transform=fig.transFigure, fill=False, linewidth=width, edgecolor=edge, zorder=5))
    fig._skip_outer_border = not card.get("outer_frame", False)


def rq1_barriers(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq1_barriers"
    fig_cfg = _bound(fig_cfg, key)
    panel_a = _panel_cfg(fig_cfg, key, "A")
    panel_b = _panel_cfg(fig_cfg, key, "B")
    grid_style = _shared(fig_cfg, key, "grid")
    types = _ranked(_read(stat_dir, _table(fig_cfg, key, "types")), "Normalized Barrier", fig_cfg, key)
    profile = _read(ready_dir, _table(fig_cfg, key, "profile"))
    categories = _item_category(profile, "Normalized Barrier", "Barrier Category")
    palette = fig_cfg["palette"]["barriers"]
    names = types["Normalized Barrier"].tolist()
    colors = [palette.get(categories.get(name), "#355C7D") for name in names]
    tasks = _tasks(analysis_cfg)
    counted = profile.dropna(subset=["Study ID", "Normalized Barrier", "Task"]).groupby(["Normalized Barrier", "Task"])["Study ID"].nunique()
    fig = plt.figure(figsize=figure_size(fig_cfg, "rq1_barriers"))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.32)
    type_ax = fig.add_subplot(grid[0])
    task_ax = fig.add_subplot(grid[1])
    type_ax.barh(np.arange(len(names)), types["Studies"], color=colors, height=0.72)
    span = float(types["Studies"].max()) if len(types) else 1
    _count_labels(type_ax, types["Studies"], types["Study prevalence %"], span)
    type_ax.set_yticks(np.arange(len(names)))
    type_ax.set_yticklabels(names)
    type_ax.set_xlim(0, span * 1.42)
    type_ax.set_xlabel(panel_a.get("xlabel", "Number of studies"))
    if panel_a.get("donut", True):
        _record_pie(type_ax, _read(stat_dir, _table(fig_cfg, key, "categories")), "Barrier Category", palette, fig_cfg, key)
    _corner(type_ax, panel_a.get("letter", "A"))
    _style(type_ax, "x")
    y = np.arange(len(names))
    task_ax.set_xlim(-0.55, len(tasks) - 0.45)
    task_ax.set_ylim(-0.6, len(names) - 0.4)
    if panel_b.get("vertical_grid", True):
        for index, task in enumerate(tasks):
            task_ax.axvline(index, color=grid_style.get("color", "#B0B0B0"), linewidth=grid_style.get("vertical_width", 1.05), zorder=0, ymin=0, ymax=1)
    if panel_b.get("horizontal_grid", True):
        for row in y:
            task_ax.axhline(row, color=grid_style.get("color", "#B0B0B0"), linewidth=grid_style.get("horizontal_width", 1.0), zorder=0)
    for row, name in enumerate(names):
        color = colors[row]
        for index, task in enumerate(tasks):
            count = int(counted.get((name, task), 0))
            task_ax.scatter(index, row, s=210, color=color, zorder=2)
            task_ax.text(index, row, str(count), ha="center", va="center", fontsize=5.5, color=_ink(color), zorder=3)
    task_ax.set_xticks(np.arange(len(tasks)))
    task_ax.set_xticklabels(tasks)
    task_ax.set_yticks(y)
    task_ax.set_yticklabels(names)
    task_ax.set_xlabel(panel_b.get("xlabel", "Task"))
    _corner(task_ax, panel_b.get("letter", "B"))
    task_ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.14, right=0.98, top=0.90, bottom=0.08, wspace=0.32)
    _frame_panels(fig, [[type_ax], [task_ax]], fig_cfg, key)
    return save_figure(fig, fig_cfg, "rq1_barriers", fig_dir)


def rq2_mitigations(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq2_mitigations"
    fig_cfg = _bound(fig_cfg, key)
    panel_a = _panel_cfg(fig_cfg, key, "A")
    panel_b = _panel_cfg(fig_cfg, key, "B")
    strategies = _ranked(_read(stat_dir, _table(fig_cfg, key, "strategies")), "Mitigation Strategy", fig_cfg, key)
    barriers = _ranked(_read(stat_dir, _table(fig_cfg, key, "types")), "Normalized Barrier", fig_cfg, key)
    profile = _read(ready_dir, _table(fig_cfg, key, "mitigation_profile"))
    barrier_profile = _read(ready_dir, _table(fig_cfg, key, "barrier_profile"))
    categories = _item_category(profile, "Mitigation Strategy", "Mitigation Category")
    palette = fig_cfg["palette"]["mitigations"]
    names = strategies["Mitigation Strategy"].tolist()
    barrier_names = barriers["Normalized Barrier"].tolist()
    colors = [palette.get(categories.get(name), "#355C7D") for name in names]
    barrier_rows = barrier_profile[["Study ID", "Normalized Barrier"]].dropna().drop_duplicates()
    strategy_rows = profile[["Study ID", "Mitigation Strategy"]].dropna().drop_duplicates()
    joined = barrier_rows.merge(strategy_rows, on="Study ID")
    pair_counts = joined.groupby(["Normalized Barrier", "Mitigation Strategy"])["Study ID"].nunique()
    matrix = pair_counts.unstack(fill_value=0).reindex(index=list(reversed(barrier_names)), columns=names).fillna(0)
    fig = plt.figure(figsize=figure_size(fig_cfg, "rq2_mitigations"))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.35], wspace=0.28)
    strategy_ax = fig.add_subplot(grid[0])
    heat_ax = fig.add_subplot(grid[1])
    strategy_ax.barh(np.arange(len(names)), strategies["Studies"], color=colors, height=0.72)
    span = float(strategies["Studies"].max()) if len(strategies) else 1
    _count_labels(strategy_ax, strategies["Studies"], strategies["Study prevalence %"], span)
    strategy_ax.set_yticks(np.arange(len(names)))
    strategy_ax.set_yticklabels(names)
    strategy_ax.set_xlim(0, span * 1.48)
    strategy_ax.set_xlabel(panel_a.get("xlabel", "Number of studies"))
    if panel_a.get("donut", True):
        _record_pie(strategy_ax, _read(stat_dir, _table(fig_cfg, key, "categories")), "Mitigation Category", palette, fig_cfg, key)
    _corner(strategy_ax, panel_a.get("letter", "A"))
    _style(strategy_ax, "x")
    values = matrix.to_numpy(float)
    theme = _shared(fig_cfg, key, "theme")
    cmap = LinearSegmentedColormap.from_list("same_paper", [theme.get("heatmap_low", "#F3F7F5"), theme["primary_green"]])
    image = heat_ax.imshow(values, aspect="auto", cmap=cmap, interpolation="none", vmin=0)
    heat_ax.set_xticks(np.arange(len(matrix.columns)))
    heat_ax.set_xticklabels(matrix.columns, rotation=35, ha="right")
    heat_ax.set_yticks(np.arange(len(matrix.index)))
    heat_ax.set_yticklabels(matrix.index)
    heat_ax.set_xlabel(panel_b.get("xlabel", "Mitigation strategy"))
    _corner(heat_ax, panel_b.get("letter", "B"))
    ceiling = values.max() if values.size else 1
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            heat_ax.text(j, i, f"{int(values[i, j])}", ha="center", va="center", fontsize=5.5, color="white" if values[i, j] >= ceiling * 0.55 else "#4D4D4D")
    colorbar = fig.colorbar(image, ax=heat_ax, fraction=0.046, pad=0.02)
    colorbar.set_label(panel_b.get("colorbar", "Studies"))
    fig.subplots_adjust(left=0.12, right=0.94, top=0.90, bottom=0.24, wspace=0.28)
    _frame_panels(fig, [[strategy_ax], [heat_ax, colorbar.ax]], fig_cfg, key)
    return save_figure(fig, fig_cfg, "rq2_mitigations", fig_dir)


def _rq3_panel(fig, subspec, gains, summary, task, color, xlabel: str):
    frame = gains.loc[gains["Task"].eq(task)].sort_values("study_gain", ascending=False).reset_index(drop=True)
    if frame.empty:
        return
    count = len(frame)
    grid = subspec.subgridspec(2, 2, height_ratios=[count, 1.6], width_ratios=[1.5, 2.2], hspace=0.0, wspace=0.04)
    left = fig.add_subplot(grid[0, 0])
    middle = fig.add_subplot(grid[0, 1])
    left_summary = fig.add_subplot(grid[1, 0])
    middle_summary = fig.add_subplot(grid[1, 1])
    y = np.arange(count)
    low = min(-5, float(frame["study_gain"].min()) - 2)
    high = max(10, float(frame["study_gain"].max()) + 2)
    middle.scatter(frame["study_gain"], y, s=16, marker="s", color=color, zorder=3)
    middle.axvline(0, linestyle="--", color="black", linewidth=0.8)
    middle.set_ylim(-0.5, count - 0.5)
    middle.invert_yaxis()
    middle.set_xlim(low, high)
    middle.set_yticks([])
    middle.tick_params(axis="x", labelbottom=False, length=0)
    middle.grid(True, axis="x", color="#E3E3E3", linewidth=0.5)
    middle.set_title(task, loc="center", fontweight="bold", fontsize=9, pad=8)
    left.set_xlim(0, 1)
    left.set_ylim(-0.5, count - 0.5)
    left.invert_yaxis()
    left.axis("off")
    for position, study_id in zip(y, frame["Study ID"]):
        left.text(0.02, position, study_id, fontsize=4.4, va="center")
    for axis in (left_summary, middle_summary):
        axis.set_facecolor("#E7E7E7")
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_visible(False)
    left_summary.set_xticks([])
    left_summary.text(0.02, 0.5, "Median", va="center", fontweight="bold", fontsize=6, transform=left_summary.transAxes)
    middle_summary.set_xlim(low, high)
    middle_summary.set_ylim(0, 1)
    middle_summary.axvline(0, linestyle="--", color="black", linewidth=0.8)
    median = float(summary["Median gain (pp)"])
    ci_low = float(summary["Bootstrap CI low"])
    ci_high = float(summary["Bootstrap CI high"])
    _forest(middle_summary, median, ci_low, ci_high, 0.5, color, marker="D", ms=5)
    middle_summary.set_xlabel(xlabel)
    middle_summary.text(0.99, 0.5, f"{median:.2f} [{ci_low:.2f}, {ci_high:.2f}]", va="center", ha="right", fontsize=6, fontweight="bold", transform=middle_summary.transAxes)


def rq3_gains(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq3_gains"
    fig_cfg = _bound(fig_cfg, key)
    gains = _read(stat_dir, _table(fig_cfg, key, "gains"))
    synthesis = _read(stat_dir, _table(fig_cfg, key, "synthesis")).set_index("Task")
    tasks = _tasks(analysis_cfg)
    xlabel = _panel_cfg(fig_cfg, key, "A").get("xlabel", "Signed gain (pp)")
    fig = plt.figure(figsize=figure_size(fig_cfg, key))
    outer = fig.add_gridspec(1, len(tasks), wspace=0.16)
    for index, task in enumerate(tasks):
        _rq3_panel(fig, outer[index], gains, synthesis.loc[task], task, _task_color(fig_cfg, task), xlabel)
    fig.subplots_adjust(top=0.94, bottom=0.08, left=0.03, right=0.99)
    return save_figure(fig, fig_cfg, "rq3_gains", fig_dir)


def rq4_moderators(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq4_moderators"
    fig_cfg = _bound(fig_cfg, key)
    panel_a = _panel_cfg(fig_cfg, key, "A")
    panel_b = _panel_cfg(fig_cfg, key, "B")
    panel_c = _panel_cfg(fig_cfg, key, "C")
    gains = _read(stat_dir, _table(fig_cfg, key, "gains"))
    master = _read(ready_dir, _table(fig_cfg, key, "master"))[["Study ID", "Dataset Size (numeric)"]]
    frame = gains.merge(master, on="Study ID", how="left")
    frame["Dataset Size (numeric)"] = pd.to_numeric(frame["Dataset Size (numeric)"], errors="coerce")
    environment = _read(stat_dir, _table(fig_cfg, key, "environment"))
    tasks = _tasks(analysis_cfg)
    minimum = int(analysis_cfg["analysis"]["minimum_regression_studies"])
    fig = plt.figure(figsize=figure_size(fig_cfg, "rq4_moderators"))
    grid = fig.add_gridspec(3, len(tasks), height_ratios=[1.1, 1.1, 0.9], hspace=0.55, wspace=0.28)
    for column, task in enumerate(tasks):
        color = _task_color(fig_cfg, task)
        baseline = frame.loc[frame["Task"].eq(task)].dropna(subset=["study_baseline", "study_gain"])
        baseline_ax = fig.add_subplot(grid[0, column])
        baseline_ax.scatter(baseline["study_baseline"], baseline["study_gain"], color=color, s=12, alpha=0.75, edgecolors="none")
        if len(baseline) >= minimum and baseline["study_baseline"].nunique() >= 2:
            grid_x = np.linspace(baseline["study_baseline"].min(), baseline["study_baseline"].max(), 80)
            line, low, high = _regression(baseline["study_baseline"].to_numpy(float), baseline["study_gain"].to_numpy(float), grid_x)
            baseline_ax.plot(grid_x, line, color=color, lw=1.4)
            if low is not None:
                baseline_ax.fill_between(grid_x, low, high, color=color, alpha=0.15)
        baseline_ax.axhline(0, linestyle="--", color="#7A7A7A", lw=0.8)
        baseline_ax.set_title(task, fontweight="bold", fontsize=8)
        baseline_ax.set_xlabel(panel_a.get("xlabel", "Baseline (%)"))
        if column == 0:
            baseline_ax.set_ylabel(panel_a.get("ylabel", "Signed gain (pp)"))
        _style(baseline_ax, "both")
        size = frame.loc[frame["Task"].eq(task) & frame["Dataset Size (numeric)"].gt(0)].dropna(subset=["study_gain"])
        size_ax = fig.add_subplot(grid[1, column])
        size_ax.scatter(size["Dataset Size (numeric)"], size["study_gain"], color=color, s=12, alpha=0.75, edgecolors="none")
        if len(size) >= minimum and size["Dataset Size (numeric)"].nunique() >= 2:
            logged = np.log10(size["Dataset Size (numeric)"].to_numpy(float))
            grid_x = np.linspace(logged.min(), logged.max(), 80)
            line, low, high = _regression(logged, size["study_gain"].to_numpy(float), grid_x)
            size_ax.plot(10 ** grid_x, line, color=color, lw=1.4)
            if low is not None:
                size_ax.fill_between(10 ** grid_x, low, high, color=color, alpha=0.15)
        size_ax.axhline(0, linestyle="--", color="#7A7A7A", lw=0.8)
        size_ax.set_xscale("log")
        size_ax.set_xlabel(panel_b.get("xlabel", "Dataset size"))
        if column == 0:
            size_ax.set_ylabel(panel_b.get("ylabel", "Signed gain (pp)"))
        _style(size_ax, "both")
    env_ax = fig.add_subplot(grid[2, :])
    labels = []
    for task in tasks:
        levels = environment.loc[environment["Task"].eq(task)].sort_values("Median gain (pp)")
        for _, row in levels.iterrows():
            labels.append((task, row))
    for position, (task, row) in enumerate(labels):
        _forest(env_ax, float(row["Median gain (pp)"]), float(row["Q1"]), float(row["Q3"]), position, _task_color(fig_cfg, task))
    env_ax.axvline(0, linestyle="--", color="#7A7A7A", lw=0.8)
    env_ax.set_yticks(np.arange(len(labels)))
    env_ax.set_yticklabels([f"{task}: {row['Environment']}" for task, row in labels])
    env_ax.set_xlabel(panel_c.get("xlabel", "Median gain (pp)"))
    _style(env_ax, "x")
    fig.subplots_adjust(left=0.18, right=0.98, top=0.96, bottom=0.08, hspace=0.55, wspace=0.28)
    return save_figure(fig, fig_cfg, "rq4_moderators", fig_dir)


def _side_note(ax, y, text, color) -> None:
    ax.text(1.02, y, text, transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=6.5, color=color, clip_on=False)


def rq5_credibility(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq5_credibility"
    fig_cfg = _bound(fig_cfg, key)
    spec = _spec(fig_cfg, key)
    panel_a = _panel_cfg(fig_cfg, key, "A")
    panel_b = _panel_cfg(fig_cfg, key, "B")
    quality = _read(stat_dir, _table(fig_cfg, key, "quality"))
    sensitivity = _read(stat_dir, _table(fig_cfg, key, "sensitivity"))
    criteria = spec.get("criteria", ["Independent Test Set", "Data Leakage Prevented", "Appropriate Metrics", "Limitations Discussed", "Related Samples Separated"])
    judgments = spec.get("judgments", ["Yes", "Partial", "Unclear", "No", "Not reported"])
    labels = {
        "Independent Test Set": "Independent test set",
        "Data Leakage Prevented": "Data leakage prevented",
        "Appropriate Metrics": "Appropriate metrics",
        "Related Samples Separated": "Related samples separated",
        "Limitations Discussed": "Limitations discussed",
    }
    heat = quality.loc[quality["Criterion"].isin(criteria)].pivot_table(index="Criterion", columns="Judgment", values="Percent", aggfunc="sum", fill_value=0)
    heat = heat.reindex(index=criteria, columns=judgments, fill_value=0)
    heat.index = [labels.get(value, value) for value in heat.index]
    excluded = set(spec.get("exclude_scenarios", ["mean_within_study"]))
    scenarios = [scenario for scenario in analysis_cfg.get("sensitivity_scenarios", []) if scenario not in excluded]
    scenario_labels = {
        "all_selected_comparisons": "All selected comparisons",
        "exclude_high_risk": "Exclude high risk",
        "independent_test_set_only": "Independent test set only",
        "leakage_prevented_only": "Leakage prevented only",
        "related_samples_separated_only": "Related samples separated only",
        "all_credibility_criteria_met": "All credibility criteria met",
        "exclude_extreme_gains": "Exclude extreme gains",
    }
    fig = plt.figure(figsize=figure_size(fig_cfg, "rq5_credibility"))
    grid = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.7], hspace=0.42)
    quality_ax = fig.add_subplot(grid[0])
    lower = grid[1].subgridspec(1, 2, width_ratios=[4.4, 0.9], wspace=0.04)
    forest_ax = fig.add_subplot(lower[0])
    count_ax = fig.add_subplot(lower[1], sharey=forest_ax)
    theme = _shared(fig_cfg, key, "theme")
    cmap = LinearSegmentedColormap.from_list("quality", [theme.get("quality_low", "#EEF5F1"), theme["primary_green"]])
    image = quality_ax.imshow(heat.to_numpy(float), aspect="auto", cmap=cmap, vmin=0, vmax=100)
    quality_ax.set_xticks(np.arange(len(judgments)))
    quality_ax.set_xticklabels(judgments, rotation=20, ha="right")
    quality_ax.set_yticks(np.arange(len(heat.index)))
    quality_ax.set_yticklabels(heat.index)
    quality_ax.set_xlabel(panel_a.get("xlabel", "Evidence-quality judgment"))
    _corner(quality_ax, panel_a.get("letter", "A"))
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            value = float(heat.iloc[i, j])
            if value > 0:
                quality_ax.text(j, i, f"{int(round(value))}%", ha="center", va="center", fontsize=6.2, color="white" if value >= 45 else "#4D4D4D")
    colorbar = fig.colorbar(image, ax=quality_ax, fraction=0.03, pad=0.02)
    colorbar.set_label(panel_a.get("colorbar", "Studies (%)"))
    tasks = _tasks(analysis_cfg)
    positions = np.arange(len(scenarios))[::-1]
    offsets = {task: offset for task, offset in zip(tasks, (0.22, 0.0, -0.22))}
    for task in tasks:
        subset = sensitivity.loc[sensitivity["Task"].eq(task)]
        color = _task_color(fig_cfg, task)
        for _, row in subset.iterrows():
            if row["Scenario"] not in scenarios:
                continue
            y = positions[scenarios.index(row["Scenario"])] + offsets[task]
            studies = row["Studies"]
            if pd.notna(row["Median gain (pp)"]) and pd.notna(row["Bootstrap CI low"]) and pd.notna(studies) and float(studies) > 0:
                _forest(forest_ax, float(row["Median gain (pp)"]), float(row["Bootstrap CI low"]), float(row["Bootstrap CI high"]), y, color)
    forest_ax.axvline(0, linestyle="--", color="#7A7A7A", lw=0.8)
    forest_ax.set_yticks(positions)
    forest_ax.set_yticklabels([scenario_labels.get(scenario, scenario) for scenario in scenarios])
    forest_ax.set_xlabel(panel_b.get("xlabel", "Median gain (pp)"))
    _corner(forest_ax, panel_b.get("letter", "B"))
    _style(forest_ax, "x")
    handles = [plt.Line2D([0], [0], marker="o", color=_task_color(fig_cfg, task), lw=1.1, label=task, markersize=4) for task in tasks]
    forest_ax.legend(handles=handles, frameon=False, loc="lower right")
    count_ax.set_xlim(0, len(tasks))
    count_ax.tick_params(axis="y", left=False, labelleft=False)
    count_ax.tick_params(axis="x", bottom=False, labelbottom=False)
    for spine in count_ax.spines.values():
        spine.set_visible(False)
    for index, task in enumerate(tasks):
        count_ax.text(index + 0.5, 1.04, task[0], transform=count_ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8, fontweight="bold", color=_task_color(fig_cfg, task), clip_on=False)
    for index, task in enumerate(tasks):
        color = _task_color(fig_cfg, task)
        subset = sensitivity.loc[sensitivity["Task"].eq(task)]
        for _, row in subset.iterrows():
            if row["Scenario"] not in scenarios or pd.isna(row["Studies"]):
                continue
            count_ax.text(index + 0.5, positions[scenarios.index(row["Scenario"])], str(int(row["Studies"])), ha="center", va="center", fontsize=7, color=color)
    fig.subplots_adjust(left=0.24, right=0.96, top=0.94, bottom=0.08, hspace=0.42)
    _frame_panels(fig, [[quality_ax, colorbar.ax], [forest_ax, count_ax]], fig_cfg, key)
    return save_figure(fig, fig_cfg, "rq5_credibility", fig_dir)


def rq6_synthetic(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg):
    key = "rq6_synthetic"
    fig_cfg = _bound(fig_cfg, key)
    spec = _spec(fig_cfg, key)
    panel = _panel_cfg(fig_cfg, key, "A")
    contrast = _read(stat_dir, _table(fig_cfg, key, "contrast")).iloc[0]
    summary = _read(stat_dir, _table(fig_cfg, key, "summary"))
    subtypes = _read(stat_dir, _table(fig_cfg, key, "subtypes"))
    tasks = _tasks(analysis_cfg)
    navy = _shared(fig_cfg, key, "theme")["neutral_primary"]
    family = panel.get("family", "Synthetic Image Methods")
    rows = [(panel.get("contrast_label", family), "contrast", None)]
    for subtype in spec.get("subtype_order", ["Data Augmentation", "Synthetic Data Generation"]):
        matches = subtypes.loc[subtypes["Synthetic Type"].eq(subtype)]
        ordered = matches.set_index("Task").reindex([task for task in tasks if task in set(matches["Task"])]).dropna(subset=["Studies"]).reset_index()
        several = len(ordered) > 1
        for _, record in ordered.iterrows():
            label = f"{subtype}, {record['Task']}" if several else subtype
            rows.append((label, "subtype" if not spec.get("subtype_interval", False) else "task", record))
    for task in tasks:
        record = summary.loc[summary["Task"].eq(task) & summary["Method Family"].eq(family)]
        if record.empty:
            continue
        rows.append((f"Synthetic, {task}", "task", record.iloc[0]))
    fig = plt.figure(figsize=figure_size(fig_cfg, "rq6_synthetic"))
    ax = fig.add_subplot(111)
    positions = np.arange(len(rows))[::-1]
    for position, (label, kind, record) in zip(positions, rows):
        if kind == "contrast":
            estimate = float(contrast["Adjusted difference (pp)"])
            low = float(contrast["Bootstrap CI low"])
            high = float(contrast["Bootstrap CI high"])
            _forest(ax, estimate, low, high, position, navy, marker="D", ms=6)
            _side_note(ax, position, f"{int(contrast['Independent studies'])}  [{low:.1f}, {high:.1f}]", navy)
        elif kind == "subtype":
            ax.scatter(float(record["Median gain (pp)"]), position, marker="D", s=32, color=navy, zorder=3)
            _side_note(ax, position, str(int(record["Studies"])), navy)
        else:
            color = _task_color(fig_cfg, record["Task"])
            estimate = float(record["Median gain (pp)"])
            low = float(record["CI low"])
            high = float(record["CI high"])
            _forest(ax, estimate, low, high, position, color, marker="D", ms=5.5)
            _side_note(ax, position, f"{int(record['Studies'])}  [{low:.1f}, {high:.1f}]", color)
    ax.axvline(0, linestyle="--", color="black", lw=0.8)
    ax.set_yticks(positions)
    ax.set_yticklabels([label for label, _, _ in rows])
    ax.set_xlabel(panel.get("xlabel", "Adjusted difference or median gain (pp)"))
    _style(ax, "x")
    handles = [
        plt.Line2D([0], [0], marker="D", color=navy, lw=0, label="Overall / subtype", markersize=5),
        *[plt.Line2D([0], [0], marker="D", color=_task_color(fig_cfg, task), lw=1.1, label=task, markersize=4.5) for task in tasks],
        plt.Line2D([0], [0], color="black", lw=0.8, linestyle="--", label=panel.get("zero_label", "No difference")),
    ]
    ax.legend(handles=handles, frameon=False, loc="center left")
    fig.subplots_adjust(left=0.28, right=0.78, top=0.94, bottom=0.12)
    _frame_panels(fig, [[ax]], fig_cfg, key)
    return save_figure(fig, fig_cfg, "rq6_synthetic", fig_dir)


def create_all_figures(stat_dir: Path, ready_dir: Path, fig_dir: Path, fig_cfg: dict, analysis_cfg: dict):
    outputs = []
    notes = []
    steps = [
        ("evidence_study_profile", evidence_study_profile),
        ("evidence_geography", evidence_geography),
        ("rq1_barriers", rq1_barriers),
        ("rq2_mitigations", rq2_mitigations),
        ("rq3_gains", rq3_gains),
        ("rq4_moderators", rq4_moderators),
        ("rq5_credibility", rq5_credibility),
        ("rq6_synthetic", rq6_synthetic),
    ]
    for name, function in steps:
        result = function(stat_dir, ready_dir, fig_dir, fig_cfg, analysis_cfg)
        if name == "evidence_geography":
            paths, unmatched = result
            if unmatched:
                notes.append(unmatched_countries(", ".join(unmatched)))
        else:
            paths = result
        outputs.extend(paths)
    return outputs, notes
