import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import utils.rules_and_concepts as rules_and_concepts
import utils.constants as constants




# USAGE
# All three losses, every alpha found, grid of (metric x alpha) subplots, one line
# per architecture with a shaded std band:
# python3 plot_architecture_loss.py \
#     --group "DSL" outputs/to_send/to_send_to_GPU_onlyEquiv \
#     --group "Stratified" outputs/testRun_baselineStratified_GPU \
#     --group "Wide" outputs/testRun_1LargeLayer_GPU \
#     --out zzz_data_evaluation/architecture_comparison.png
#
# Add concept/building accuracy alongside the losses:
# python3 plot_architecture_loss.py --group ... --group ... \
#     --metrics val_loss combined_val_loss val_sat_kb concept_accuracy \
#     --out zzz_data_evaluation/architecture_comparison.png
#
# Restrict to specific alphas instead of auto-discovering every one found:
# python3 plot_architecture_loss.py --group ... --group ... --alphas 0.8 0.5 --out ...

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()

CONCEPT_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in ALL_CONCEPTS]
BUILDING_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in ALL_BUILDING_CLASSES]

SUPER_CLASSES = rules_and_concepts.get_super_classes()
SUPER_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in SUPER_CLASSES]

METRIC_LABELS = {
    "val_loss": "Validation Loss",
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


def load_metric_series(metrics_paths, metric_spec):
    """
    metric_spec: a literal metrics.csv column name, or one of
    "concept_accuracy" / "building_accuracy" / "overall_accuracy", which average
    across the relevant set of *_val_accuracy columns for that run before the
    across-run mean/std is computed.
    """
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


def plot_grid(groups, metrics, alphas, out_path):
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
                std = combined.std(axis=1, skipna=True)

                color = color_map[label]
                ax.plot(mean.index, mean.values, color=color, linewidth=2)
                ax.fill_between(mean.index, (mean - std).values, (mean + std).values,
                                 color=color, alpha=0.2, linewidth=0)

            ax.set_title(f"{METRIC_LABELS.get(metric, metric)}  (α={alpha})", fontsize=10)
            if row == n_rows - 1:
                ax.set_xlabel("Epoch")
            if col == 0:
                ax.set_ylabel(METRIC_LABELS.get(metric, metric), fontsize=9)
            ax.grid(True, alpha=0.3)

    handles = [mlines.Line2D([0], [0], color=color_map[l], lw=2, label=l) for l in arch_labels]
    fig.legend(handles=handles, loc="upper center", ncol=len(arch_labels), bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Grid of mean +/- std curves (one subplot per metric x alpha), "
                    "one line per architecture/config, each averaged across its runs."
    )
    parser.add_argument("--group", action="append", nargs=2, metavar=("LABEL", "ROOT_DIR"),
                         required=True,
                         help="Add a group: a display label and a folder containing run*_outputs "
                              "subfolders. Repeat --group for each architecture/config to compare.")
    parser.add_argument("--metrics", nargs="+", default=DEFAULT_METRICS,
                         help=f"Metrics to plot, one row each (default: {DEFAULT_METRICS}). "
                              "Add 'concept_accuracy', 'building_accuracy', or 'overall_accuracy' "
                              "to include mean per-class accuracy.")
    parser.add_argument("--alphas", nargs="+", type=float, default=None,
                         help="Alphas to plot, one column each (default: auto-discover every "
                              "alpha found across all --group folders).")
    parser.add_argument("--out", type=Path, default=Path("architecture_comparison.png"))
    args = parser.parse_args()

    groups = {label: Path(root_dir) for label, root_dir in args.group}
    alphas = args.alphas or discover_alphas(groups)
    if not alphas:
        parser.error("No alphas found across the given --group folders.")
    print(f"Alphas: {alphas}")
    print(f"Metrics: {args.metrics}")

    plot_grid(groups, args.metrics, alphas, args.out)


if __name__ == "__main__":
    main()