import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import utils.rules_and_concepts as rules_and_concepts


# USAGE
# Mean +/- std band (default):
# python3 plot_architecture_loss.py \
#     --group "DSL" ../outputs/testRun_onlyEquivalences_GPU \
#     --group "Wide" ../outputs/testRun_1LargeLayer_onlyEquivalences_GPU \
#     --out ../zzz_data_evaluation/architecture_comparison.png
#
# Every individual run's raw line instead, to sanity-check the averaging/data:
# python3 plot_architecture_loss.py --group ... --group ... --show-individual-runs --out ...

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
SUPER_CLASSES = rules_and_concepts.get_super_classes()

CONCEPT_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in ALL_CONCEPTS]
BUILDING_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in ALL_BUILDING_CLASSES]
SUPER_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in SUPER_CLASSES]

METRIC_LABELS = {
    "val_loss": "Classification Validation Loss",
    "combined_val_loss": "Combined Validation Loss",
    "train_loss": "Training Loss",
    "combined_train_loss": "Combined Training Loss",
    "val_sat_kb": "KB Satisfaction (Val)",
    "train_sat_kb": "KB Satisfaction (Train)",
    "super_accuracy": "Mean Super-Class Accuracy",
    "concept_accuracy": "Mean Concept Accuracy",
    "building_accuracy": "Mean Building Accuracy",
    "overall_accuracy": "Mean Overall Accuracy",
}

DEFAULT_METRICS = ["val_loss", "combined_val_loss", "val_sat_kb"]

BEST_EPOCH_RE = re.compile(r"Best epoch found:\s*(\d+)")


def discover_runs(root_dir, alpha_filter=None):
    root_dir = Path(root_dir)
    paths = []
    for run_dir in sorted(root_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        metrics_path = run_dir / "metrics.csv"
        if not metrics_path.exists():
            continue
        if alpha_filter is not None:
            alpha_df = pd.read_csv(metrics_path, usecols=["Alpha"])
            if alpha_df.empty:
                continue
            run_alpha = round(float(alpha_df["Alpha"].iloc[0]), 4)
            if abs(run_alpha - alpha_filter) > 1e-6:
                continue
        paths.append(metrics_path)
    return paths


def discover_alphas(groups):
    alphas = set()
    for root_dir in groups.values():
        root_dir = Path(root_dir)
        for run_dir in root_dir.iterdir():
            if not run_dir.is_dir():
                continue
            metrics_path = run_dir / "metrics.csv"
            if not metrics_path.exists():
                continue
            df = pd.read_csv(metrics_path, usecols=["Alpha"])
            if df.empty:
                continue
            alphas.add(round(float(df["Alpha"].iloc[0]), 4))
    return sorted(alphas, reverse=True)


def get_best_epoch(metrics_path):
    """Reads the run's stats.txt (sibling of metrics.csv) for 'Best epoch found: N'."""
    stats_path = metrics_path.parent / "stats.txt"
    if not stats_path.exists():
        return None
    m = BEST_EPOCH_RE.search(stats_path.read_text())
    return int(m.group(1)) if m else None


def load_metric_series(metrics_paths, metric_spec):
    series_list = []
    for i, path in enumerate(metrics_paths):
        df = pd.read_csv(path)
        df = df.drop_duplicates(subset="Epoch").set_index("Epoch")

        if metric_spec == "super_accuracy":
            cols = [c for c in SUPER_ACC_COLS if c in df.columns]
            values = df[cols].mean(axis=1)
        elif metric_spec == "concept_accuracy":
            cols = [c for c in CONCEPT_ACC_COLS if c in df.columns]
            values = df[cols].mean(axis=1)
        elif metric_spec == "building_accuracy":
            cols = [c for c in BUILDING_ACC_COLS if c in df.columns]
            values = df[cols].mean(axis=1)
        elif metric_spec == "overall_accuracy":
            cols = [c for c in df.columns if c.endswith("_val_accuracy")]
            values = df[cols].mean(axis=1)
        else:
            values = df[metric_spec]

        values.name = f"run{i}"
        series_list.append(values)
    return pd.concat(series_list, axis=1)


def nearest_value(series, epoch):
    """Value of `series` at the epoch closest to `epoch` (metrics.csv rows are every
    VALIDATION_INTERVAL epochs, so the exact best-epoch row may not exist)."""
    pos = np.abs(series.index.to_numpy() - epoch).argmin()
    return series.iloc[pos]

def plot_grid(groups, metrics, alphas, mark_best_epoch, show_individual, show_baseline_alpha,
              baseline_alpha, out_path):
    n_rows, n_cols = len(metrics), len(alphas)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 3.5 * n_rows), squeeze=False)

    colors = plt.cm.tab10.colors
    arch_labels = list(groups.keys())
    color_map = {label: colors[i % len(colors)] for i, label in enumerate(arch_labels)}

    for row, metric in enumerate(metrics):
        for col, alpha in enumerate(alphas):
            ax = axes[row][col]
            for label, root_dir in groups.items():
                metrics_paths = discover_runs(root_dir, alpha)
                if not metrics_paths:
                    print(f"[skip] {label} @ alpha={alpha}: no matching runs")
                    continue
                combined = load_metric_series(metrics_paths, metric)
                mean = combined.mean(axis=1, skipna=True)
                color = color_map[label]

                if show_individual:
                    for run_col in combined.columns:
                        run_series = combined[run_col].dropna()
                        ax.plot(run_series.index, run_series.values, color=color,
                                linewidth=1, alpha=0.5)
                    ax.plot(mean.index, mean.values, color=color, linewidth=2.5,
                             linestyle="--")
                else:
                    std = combined.std(axis=1, skipna=True)
                    ax.plot(mean.index, mean.values, color=color, linewidth=2)
                    ax.fill_between(mean.index, (mean - std).values, (mean + std).values,
                                     color=color, alpha=0.2, linewidth=0)

                if show_baseline_alpha and abs(alpha - baseline_alpha) > 1e-6:
                    baseline_paths = discover_runs(root_dir, baseline_alpha)
                    if baseline_paths:
                        baseline_mean = load_metric_series(baseline_paths, metric).mean(axis=1, skipna=True)
                        ax.plot(baseline_mean.index, baseline_mean.values, color="black",
                                linewidth=2, linestyle=":", zorder=4)
                    else:
                        print(f"[skip] {label}: no alpha={baseline_alpha} runs found for baseline reference")

                if mark_best_epoch == "each":
                    for run_idx, path in enumerate(metrics_paths):
                        best_epoch = get_best_epoch(path)
                        if best_epoch is None:
                            continue
                        run_series = combined[f"run{run_idx}"].dropna()
                        ax.scatter([best_epoch], [nearest_value(run_series, best_epoch)],
                                   color=color, edgecolor="black", zorder=5, s=40, marker="o")
                elif mark_best_epoch == "mean":
                    best_epochs = [get_best_epoch(p) for p in metrics_paths]
                    best_epochs = [e for e in best_epochs if e is not None]
                    if not best_epochs:
                        continue
                    epoch_to_mark = int(round(np.mean(best_epochs)))
                    ax.scatter([epoch_to_mark], [nearest_value(mean, epoch_to_mark)], color=color,
                               edgecolor="black", zorder=5, s=50, marker="o")

            ax.set_title(f"{METRIC_LABELS.get(metric, metric)}  (α={alpha})", fontsize=10)
            if row == n_rows - 1:
                ax.set_xlabel("Epoch")
            if col == 0:
                ax.set_ylabel(METRIC_LABELS.get(metric, metric), fontsize=9)
            ax.grid(True, alpha=0.3)

    handles = [mlines.Line2D([0], [0], color=color_map[l], lw=2, label=l) for l in arch_labels]
    if show_individual:
        handles.append(mlines.Line2D([0], [0], color="gray", lw=2.5, linestyle="--",
                                      label="mean (dashed)"))
    if show_baseline_alpha:
        handles.append(mlines.Line2D([0], [0], color="black", lw=2, linestyle=":",
                                      label=f"α={baseline_alpha:g} baseline (mean)"))
    if mark_best_epoch != "none":
        handles.append(mlines.Line2D([0], [0], marker="o", color="gray", markeredgecolor="black",
                                      linestyle="None", markersize=7,
                                      label="best epoch" + (" (mean)" if mark_best_epoch == "mean" else " (per run)")))
    fig.legend(handles=handles, loc="upper center", ncol=len(handles), bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Grid of loss/accuracy curves (one subplot per metric x alpha), one "
                    "line per architecture/config. By default shows mean +/- std across each "
                    "group's runs; --show-individual-runs plots every run's raw curve instead "
                    "(plus a dashed mean line), useful for sanity-checking the data."
    )
    parser.add_argument("--group", action="append", nargs=2, metavar=("LABEL", "ROOT_DIR"),
                         required=True,
                         help="Add a group: a display label and a folder containing run*_outputs "
                              "subfolders. Repeat --group for each architecture/config to compare.")
    parser.add_argument("--metrics", nargs="+", default=DEFAULT_METRICS,
                         help=f"Metrics to plot, one row each (default: {DEFAULT_METRICS}). "
                              "Add 'super_accuracy', 'concept_accuracy', 'building_accuracy', or "
                              "'overall_accuracy' to include mean per-class accuracy.")
    parser.add_argument("--alphas", nargs="+", type=float, default=None,
                         help="Alphas to plot, one column each (default: auto-discover every "
                              "alpha found across all --group folders).")
    parser.add_argument("--mark-best-epoch", choices=["each", "mean", "none"], default="each",
                         help="Mark each run's best epoch ('each', default; on its own raw line "
                              "if --show-individual-runs is set, otherwise interpolated onto the "
                              "mean line), only the average best epoch ('mean'), or none ('none').")
    parser.add_argument("--show-individual-runs", action="store_true",
                         help="Plot every run's raw curve (thin, semi-transparent) plus a dashed "
                              "mean line, instead of the mean +/- std band. Useful for checking "
                              "the data/averaging directly rather than trusting the aggregate.")
    parser.add_argument("--out", type=Path, default=Path("architecture_comparison.png"))
    parser.add_argument("--show-baseline-alpha", action="store_true",
                         help="On every subplot except the baseline alpha's own column, draw "
                              "each group's baseline-alpha mean as a thin dotted reference line "
                              "(no std band), so you can compare each alpha directly against its "
                              "own group's baseline without switching subplots.")
    parser.add_argument("--baseline-alpha", type=float, default=1.0,
                         help="Which alpha counts as the baseline for --show-baseline-alpha (default: 1.0).")
    args = parser.parse_args()

    groups = {label: Path(root_dir) for label, root_dir in args.group}
    alphas = args.alphas or discover_alphas(groups)
    if not alphas:
        parser.error("No alphas found across the given --group folders.")
    print(f"Alphas: {alphas}")
    print(f"Metrics: {args.metrics}")

    plot_grid(groups, args.metrics, alphas, args.mark_best_epoch, args.show_individual_runs,
              args.show_baseline_alpha, args.baseline_alpha, args.out)


if __name__ == "__main__":
    main()