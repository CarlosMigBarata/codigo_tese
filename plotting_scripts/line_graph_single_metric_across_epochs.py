import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# USAGE
# One line + shaded std band per architecture, averaged across each architecture's runs.
# python3 plot_architecture_loss.py \
#     --group "DSL" outputs/to_send/to_send_to_GPU_onlyEquiv \
#     --group "Stratified" outputs/testRun_baselineStratified_GPU \
#     --group "Wide" outputs/testRun_1LargeLayer_GPU \
#     --alpha 0.8 \
#     --column val_loss --ylabel "Validation Loss" --title "Validation Loss by Architecture" \
#     --out zzz_data_evaluation/architecture_val_loss.png
#
# Repeat with --column combined_val_loss or --column val_sat_kb for other curves.


def discover_runs(root_dir, alpha_filter=None):
    """Find run*_outputs subfolders with a metrics.csv, optionally filtered by Alpha."""
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


def load_metric_series(metrics_paths, column):
    """
    Returns a DataFrame indexed by Epoch, one column per run. Runs of different
    lengths (early stopping) are aligned by Epoch via outer join -- shorter runs
    leave NaN past their last epoch, which mean/std below simply skip.
    """
    series_list = []
    for i, path in enumerate(metrics_paths):
        df = pd.read_csv(path, usecols=["Epoch", column])
        df = df.drop_duplicates(subset="Epoch").set_index("Epoch")[column]
        df.name = f"run{i}"
        series_list.append(df)
    return pd.concat(series_list, axis=1)


def plot_groups(groups, alpha_filter, column, ylabel, title, out_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10.colors

    for i, (label, root_dir) in enumerate(groups.items()):
        metrics_paths = discover_runs(root_dir, alpha_filter)
        if not metrics_paths:
            print(f"[skip] {label}: no matching metrics.csv found under {root_dir}")
            continue
        print(f"[{label}] {len(metrics_paths)} run(s)")

        combined = load_metric_series(metrics_paths, column)
        mean = combined.mean(axis=1, skipna=True)
        std = combined.std(axis=1, skipna=True)

        color = colors[i % len(colors)]
        ax.plot(mean.index, mean.values, label=label, color=color, linewidth=2)
        ax.fill_between(mean.index, (mean - std).values, (mean + std).values,
                         color=color, alpha=0.2, linewidth=0)

    ax.set_xlabel("Epoch")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot mean +/- std validation loss/metric curves across epochs, "
                    "one line per architecture/config, each averaged across its runs."
    )
    parser.add_argument("--group", action="append", nargs=2, metavar=("LABEL", "ROOT_DIR"),
                         required=True,
                         help="Add a group: a display label and a folder containing run*_outputs "
                              "subfolders. Repeat --group for each architecture/config to compare.")
    parser.add_argument("--alpha", type=float, default=None,
                         help="Only include runs with this alpha (matches metrics.csv's Alpha "
                              "column). Omit to include every run found, regardless of alpha.")
    parser.add_argument("--column", default="val_loss",
                         help="Column in metrics.csv to plot (default: val_loss). Other useful "
                              "options: combined_val_loss, train_loss, combined_train_loss, val_sat_kb.")
    parser.add_argument("--ylabel", default=None, help="Y-axis label (default: same as --column).")
    parser.add_argument("--title", default="Validation Loss by Architecture")
    parser.add_argument("--out", type=Path, default=Path("architecture_loss_comparison.png"))
    args = parser.parse_args()

    groups = {label: Path(root_dir) for label, root_dir in args.group}
    ylabel = args.ylabel or args.column

    plot_groups(groups, args.alpha, args.column, ylabel, args.title, args.out)


if __name__ == "__main__":
    main()