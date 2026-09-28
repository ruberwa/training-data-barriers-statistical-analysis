from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

MM_TO_INCH = 1 / 25.4


def setup_style(cfg: dict) -> None:
    theme = cfg.get("theme", {})
    plt.rcParams.update({
        "font.family": theme.get("font_family", "Arial"),
        "axes.labelsize": theme.get("axis_label_pt", 8.5),
        "xtick.labelsize": theme.get("tick_label_pt", 7),
        "ytick.labelsize": theme.get("tick_label_pt", 7),
        "legend.fontsize": theme.get("legend_pt", 7),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": theme.get("background", "white"),
        "axes.facecolor": theme.get("background", "white"),
        "savefig.facecolor": theme.get("background", "white"),
    })


def figure_size(fig_cfg: dict, key: str) -> tuple[float, float]:
    spec = fig_cfg["figures"].get(key, {})
    return spec.get("width_mm", 180) * MM_TO_INCH, spec.get("height_mm", 120) * MM_TO_INCH


def _ensure_figure_border(fig, linewidth: float = 0.8, edgecolor: str = "#8C8C8C") -> None:
    if getattr(fig, "_outer_border_added", False):
        return
    rect = Rectangle((0.005, 0.005), 0.99, 0.99, transform=fig.transFigure, fill=False, linewidth=linewidth, edgecolor=edgecolor, zorder=1000)
    fig.add_artist(rect)
    fig._outer_border_added = True


def save_figure(fig, fig_cfg: dict, key: str, figures_dir: Path) -> list[Path]:
    spec = fig_cfg["figures"].get(key, {})
    filename = spec.get("filename", key)
    outputs = []
    outcfg = fig_cfg.get("output", {})
    formats = outcfg.get("formats", {})
    bbox = outcfg.get("bbox_inches", "tight")
    pad = outcfg.get("pad_inches", 0.05)

    def output_path(format_name: str, extension: str | None = None) -> Path:
        format_cfg = formats.get(format_name, {})
        folder = format_cfg.get("folder", format_name)
        directory = figures_dir / folder
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{filename}.{extension or format_name}"

    if spec.get("outer_frame", True) and not getattr(fig, "_skip_outer_border", False):
        _ensure_figure_border(fig)
    if formats.get("png", {}).get("enabled", True):
        path = output_path("png")
        fig.savefig(path, dpi=formats.get("png", {}).get("dpi", 300), bbox_inches=bbox, pad_inches=pad)
        outputs.append(path)
    if formats.get("pdf", {}).get("enabled", True):
        path = output_path("pdf")
        fig.savefig(path, bbox_inches=bbox, pad_inches=pad)
        outputs.append(path)
    if formats.get("tiff", {}).get("enabled", False):
        path = output_path("tiff", "tiff")
        fig.savefig(path, dpi=formats.get("tiff", {}).get("dpi", 600), bbox_inches=bbox, pad_inches=pad, pil_kwargs={"compression": formats.get("tiff", {}).get("compression", "tiff_adobe_deflate")})
        outputs.append(path)
    plt.close(fig)
    return outputs
