import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import utils.rules_and_concepts as rules_and_concepts

# USAGE
# python3 plot_sample_efficiency.py \
#     --size 1000  ../outputs/testRun_sampleEff_1000_GPU \
#     --size 2000  ../outputs/testRun_sampleEff_2000_GPU \
#     --size 4000  ../outputs/testRun_sampleEff_4000_GPU \
#     --size 8000  ../outputs/testRun_sampleEff_8000_GPU \
#     --size 12000 ../outputs/testRun_sampleEff_12000_GPU \
#     --size 16000 ../outputs/testRun_sampleEff_16000_GPU \
#     --out ../zzz_data_evaluation/sample_efficiency_by_size.png

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
SUPER_CLASSES = rules_and_concepts.get_super_classes()

BUILDING_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in ALL_BUILDING_CLASSES]
SUPER_ACC_COLS = [f"{name.lower()}_val_accuracy" for name in SUPER_CLASSES]

METRIC_LABELS = {
    "val_loss": "Classification Validation Loss",
    "val_sat_kb": "KB Satisfaction (Val)",
    "building_super_accuracy": "Mean Building + Super-Class Accuracy",
}

DEFAULT_METRICS = ["val_loss", "val_sat_kb", "building_super_accuracy"]

BEST_EPOCH_RE = re.compile(r"Best epoch found:\s*(\d+)")


def discover_runs_by_alpha(root_dir):
    root_dir = Path(root_dir)
    groups = {}
    for run_dir in sorted(root_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        metrics_path = run_dir / "metrics.csv"
        if not metrics_path.exists():
            continue
        df = pd.read_csv(metrics_path, usecols=["Alpha"])
        if df.empty:
            continue
        alpha = round(float(df["Alpha"].iloc[0]), 4)
        groups.setdefault(alpha, []).append(run_dir)
    return groups


def get_best_epoch(run_dir):
    stats_path = run_dir / "stats.txt"
    if not stats_path.exists():
        return None
    m = BEST_EPOCH_RE.search(stats_path.read_text())
    return int(m.group(1)) if m else None


def value_at_best_epoch(run_dir, metric_spec):
    df = pd.read_csv(run_dir / "metrics.csv")
    df = df.drop_duplicates(subset="Epoch").set_index("Epoch")

    if metric_spec == "building_super_accuracy":
        cols = [c for c in (BUILDING_ACC_COLS + SUPER_ACC_COLS) if c in df.columns]
        series = df[cols].mean(axis=1)
    else:
        series = df[metric_spec]

    best_epoch = get_best_epoch(run_dir)
    if best_epoch is None:
        return None
    pos = np.abs(series.index.to_numpy() - best_epoch).argmin()
    return series.iloc[pos]


def plot_by_size(sizes, metrics, alphas, out_path):
    n_metrics = len(metrics)
    fig, axes = plt.subplots(1, n_metrics, figsize=(6.5 * n_metrics, 4.5), squeeze=False)
    axes = axes[0]

    colors = plt.cm.tab10.colors
    color_map = {a: colors[i % len(colors)] for i, a in enumerate(alphas)}

    size_labels = [label for label, _ in sizes]
    x = np.arange(len(sizes))

    for col, metric in enumerate(metrics):
        ax = axes[col]
        for alpha in alphas:
            y = []
            for label, root_dir in sizes:
                groups = discover_runs_by_alpha(root_dir)
                run_dirs = groups.get(alpha, [])
                if not run_dirs:
                    print(f"[skip] size={label} alpha={alpha}: no matching runs")
                    y.append(np.nan)
                    continue
                vals = [value_at_best_epoch(rd, metric) for rd in run_dirs]
                vals = [v for v in vals if v is not None]
                y.append(np.mean(vals) if vals else np.nan)
            ax.plot(x, y, marker="o", color=color_map[alpha], linewidth=2, label=f"alpha={alpha:g}")

        ax.set_xticks(x)
        ax.set_xticklabels(size_labels)
        ax.set_xlabel("Training set size")
        ax.set_title(METRIC_LABELS.get(metric, metric), fontsize=10)
        ax.grid(True, alpha=0.3)
        if col == 0:
            ax.set_ylabel("Value")

    axes[0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Sample efficiency plot: x-axis is training-set size, one line per alpha, "
                    "one subplot per metric, value taken at each run's own best epoch and "
                    "averaged over the 3 seeds per (size, alpha) combination."
    )
    parser.add_argument("--size", action="append", nargs=2, metavar=("LABEL", "ROOT_DIR"),
                         required=True,
                         help="Add a training-set size: a display label and its folder "
                              "(containing run*_outputs subfolders). Repeat for each size, "
                              "smallest to largest.")
    parser.add_argument("--metrics", nargs="+", default=DEFAULT_METRICS,
                         help=f"Metrics to plot, one subplot each (default: {DEFAULT_METRICS}).")
    parser.add_argument("--alphas", nargs="+", type=float, default=[1.0, 0.8, 0.5],
                         help="Alphas to plot as separate lines (default: 1.0 0.8 0.5).")
    parser.add_argument("--out", type=Path, default=Path("sample_efficiency_by_size.png"))
    args = parser.parse_args()

    sizes = [(label, Path(root_dir)) for label, root_dir in args.size]
    # sort by numeric value of the label, ascending (smallest dataset first)
    sizes.sort(key=lambda s: int(s[0]))

    plot_by_size(sizes, args.metrics, args.alphas, args.out)


if __name__ == "__main__":
    main()