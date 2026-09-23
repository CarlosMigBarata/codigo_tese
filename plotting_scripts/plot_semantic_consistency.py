import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SENTINEL = -2.0


def discover_runs(root_dir, alpha_filter=None):
    root_dir = Path(root_dir)
    paths = []
    for run_dir in sorted(root_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        consistency_path = run_dir / "consistency_validation_val.txt"
        if not consistency_path.exists():
            continue
        if alpha_filter is not None:
            metrics_path = run_dir / "metrics.csv"
            if not metrics_path.exists():
                continue
            alpha_df = pd.read_csv(metrics_path, usecols=["Alpha"])
            if alpha_df.empty:
                continue
            run_alpha = round(float(alpha_df["Alpha"].iloc[0]), 4)
            if abs(run_alpha - alpha_filter) > 1e-6:
                continue
        paths.append(consistency_path)
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


def parse_consistency_file(path, exclude_sentinel=True):
    rules = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if " | consistency=" not in line:
                continue
            name, rest = line.split(" | consistency=", 1)
            name = name.strip()
            try:
                value = float(rest.split("|")[0].strip())
            except ValueError:
                continue
            if exclude_sentinel and abs(value - SENTINEL) < 1e-6:
                continue
            rules[name] = value
    return rules


def mean_consistency_for_run(path):
    active_rules = parse_consistency_file(path, exclude_sentinel=True)
    all_rules = parse_consistency_file(path, exclude_sentinel=False)
    if not active_rules:
        return None, 0, len(all_rules)
    return float(np.mean(list(active_rules.values()))), len(active_rules), len(all_rules)


def plot_bar_chart(groups, alphas, out_path):
    fig, ax = plt.subplots(figsize=(3 * len(alphas) + 2, 5))
    arch_labels = list(groups.keys())
    n_arch = len(arch_labels)
    bar_width = 0.8 / n_arch
    colors = plt.cm.tab10.colors
    x = np.arange(len(alphas))

    for i, label in enumerate(arch_labels):
        means, stds = [], []
        for alpha in alphas:
            paths = discover_runs(groups[label], alpha)
            run_means = []
            n_active_total, n_all_total = 0, 0
            for p in paths:
                m, n_active, n_all = mean_consistency_for_run(p)
                n_active_total += n_active
                n_all_total += n_all
                if m is not None:
                    run_means.append(m)
            if run_means:
                means.append(np.mean(run_means))
                stds.append(np.std(run_means))
            else:
                means.append(0.0)
                stds.append(0.0)
            print(f"[{label}] alpha={alpha}: {n_active_total}/{n_all_total} rule-instances "
                  f"actively engaged (rest hit the always-vacuous sentinel)")
        offset = (i - (n_arch - 1) / 2) * bar_width
        ax.bar(x + offset, means, bar_width, yerr=stds, label=label,
               color=colors[i % len(colors)], capsize=3)

    ax.set_xticks(x)
    ax.set_xticklabels([f"α={a}" for a in alphas])
    ax.set_ylabel("Mean Semantic Consistency\n(always-vacuous rules excluded)")
    ax.set_title("Semantic Consistency by Architecture and Alpha")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bar chart of mean semantic consistency (from consistency_validation_val.txt), "
                    "grouped by alpha, one bar per architecture/config, averaged across each group's "
                    "runs. Rules with consistency=-2.0000 (never actively/non-vacuously satisfied, "
                    "only ever trivially true) are excluded from the average -- that's a sentinel for "
                    "a degenerate always-false solution, not a real consistency score."
    )
    parser.add_argument("--group", action="append", nargs=2, metavar=("LABEL", "ROOT_DIR"), required=True)
    parser.add_argument("--alphas", nargs="+", type=float, default=None)
    parser.add_argument("--out", type=Path, default=Path("semantic_consistency.png"))
    args = parser.parse_args()

    groups = {label: Path(root_dir) for label, root_dir in args.group}
    alphas = args.alphas or discover_alphas(groups)
    if not alphas:
        parser.error("No alphas found across the given --group folders.")
    print(f"Alphas: {alphas}")

    plot_bar_chart(groups, alphas, args.out)


if __name__ == "__main__":
    main()