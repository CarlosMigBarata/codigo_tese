import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Hardcoded from the three "fixed 2x negative, increasing positive" WallSign tables.
DATA = {
    "1xPos_2xNeg": {
        "buildings": {
            "Cafe":       {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
            "Restaurant": {(0.8, "train"): 3.83,  (0.8, "val"): 4.04,  (0.5, "train"): 10.97, (0.5, "val"): 11.78},
            "Store":      {(0.8, "train"): 12.51, (0.8, "val"): 13.36, (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
        },
        "concepts": {
            "Awning":         {(0.8, "train"): 19.19, (0.8, "val"): 19.84, (0.5, "train"): 24.85, (0.5, "val"): 26.21},
            "Billboard":      {(0.8, "train"): 12.88, (0.8, "val"): 12.76, (0.5, "train"): 32.84, (0.5, "val"): 32.43},
            "VendingMachine": {(0.8, "train"): 36.31, (0.8, "val"): 36.05, (0.5, "train"): 16.04, (0.5, "val"): 15.88},
            "WallSign":       {(0.8, "train"): 35.84, (0.8, "val"): 34.85, (0.5, "train"): 23.23, (0.5, "val"): 22.68},
        },
    },
    "2xPos_2xNeg": {
        "buildings": {
            "Cafe":       {(0.8, "train"): 7.80,  (0.8, "val"): 7.73,  (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
            "Hotel":      {(0.8, "train"): 26.43, (0.8, "val"): 26.04, (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
            "Restaurant": {(0.8, "train"): 10.12, (0.8, "val"): 10.58, (0.5, "train"): 3.83,  (0.5, "val"): 4.04},
            "Store":      {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 20.89, (0.5, "val"): 21.92},
        },
        "concepts": {
            "Awning":         {(0.8, "train"): 17.82, (0.8, "val"): 18.18, (0.5, "train"): 35.46, (0.5, "val"): 36.88},
            "Billboard":      {(0.8, "train"): 69.11, (0.8, "val"): 68.75, (0.5, "train"): 12.79, (0.5, "val"): 12.55},
            "VendingMachine": {(0.8, "train"): 17.35, (0.8, "val"): 17.45, (0.5, "train"): 52.88, (0.5, "val"): 52.45},
            "WallSign":       {(0.8, "train"): 58.70, (0.8, "val"): 57.00, (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
        },
    },
    "3xPos_2xNeg": {
        "buildings": {
            "Cafe":           {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 7.80,  (0.5, "val"): 7.73},
            "Hotel":          {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 7.35,  (0.5, "val"): 7.05},
            "Restaurant":     {(0.8, "train"): 14.14, (0.8, "val"): 14.94, (0.5, "train"): 3.83,  (0.5, "val"): 4.04},
            "Store":          {(0.8, "train"): 3.37,  (0.8, "val"): 3.62,  (0.5, "train"): 12.10, (0.5, "val"): 12.60},
            "MiscCommercial": {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 0.00,  (0.5, "val"): 0.00},
        },
        "concepts": {
            "Awning":         {(0.8, "train"): 28.65, (0.8, "val"): 29.68, (0.5, "train"): 44.07, (0.5, "val"): 44.99},
            "Billboard":      {(0.8, "train"): 40.53, (0.8, "val"): 40.08, (0.5, "train"): 25.58, (0.5, "val"): 25.11},
            "Table":          {(0.8, "train"): 47.01, (0.8, "val"): 47.21, (0.5, "train"): 26.12, (0.5, "val"): 26.02},
            "VendingMachine": {(0.8, "train"): 17.70, (0.8, "val"): 17.74, (0.5, "train"): 53.92, (0.5, "val"): 53.80},
            "WallSign":       {(0.8, "train"): 0.00,  (0.8, "val"): 0.00,  (0.5, "train"): 23.23, (0.5, "val"): 22.68},
        },
    },
}

TEST_ORDER = ["1xPos_2xNeg", "2xPos_2xNeg", "3xPos_2xNeg"]
TEST_LABELS = {
    "1xPos_2xNeg": "1x positive, 2x negative",
    "2xPos_2xNeg": "2x positive, 2x negative",
    "3xPos_2xNeg": "3x positive, 2x negative",
}
ALPHA_COLORS = {0.8: "#1f77b4", 0.5: "#ff7f0e"}


def plot_wallsign_focus(out_path, split):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    x = np.arange(len(TEST_ORDER))
    width = 0.35

    for i, alpha in enumerate([0.8, 0.5]):
        values = [DATA[t]["concepts"]["WallSign"][(alpha, split)] for t in TEST_ORDER]
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, values, width, label=f"α={alpha:g}", color=ALPHA_COLORS[alpha])
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels([TEST_LABELS[t] for t in TEST_ORDER])
    ax.set_ylabel(f"WallSign F1 ({split}, %)")
    ax.set_title("WallSign recovery: fixed 2x negative, increasing positive occurrences")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def plot_test_detail(test_name, out_path, split):
    test_data = DATA[test_name]
    building_names = list(test_data["buildings"].keys())
    concept_names = list(test_data["concepts"].keys())
    names = building_names + concept_names

    fig, ax = plt.subplots(figsize=(1.1 * len(names) + 2, 4.5))
    x = np.arange(len(names))
    width = 0.35

    for i, alpha in enumerate([0.8, 0.5]):
        values = []
        for name in names:
            group = "buildings" if name in test_data["buildings"] else "concepts"
            values.append(test_data[group][name][(alpha, split)])
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, values, width, label=f"α={alpha:g}", color=ALPHA_COLORS[alpha])
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7)

    xticklabels = [f"$\\bf{{{n}}}$" if n == "WallSign" else n for n in names]
    ax.set_xticks(x)
    ax.set_xticklabels(xticklabels, rotation=30, ha="right")
    ax.axvline(len(building_names) - 0.5, color="gray", linestyle="--", linewidth=1)
    ax.set_ylabel(f"F1 ({split}, %)")
    ax.set_title(f"{TEST_LABELS[test_name]} ({test_name})")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bar charts for the second WallSign experiment (fixed 2x negative "
                    "occurrences, increasing positive occurrences from 1 to 3). Produces one "
                    "WallSign-only comparison chart across all three tests, plus one detail "
                    "chart per test."
    )
    parser.add_argument("--split", choices=["train", "val"], default="val")
    parser.add_argument("--out-dir", default=".", help="Directory to save the charts in.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_wallsign_focus(out_dir / f"wallsign_negfixed_focus_{args.split}.png", args.split)
    for test_name in TEST_ORDER:
        plot_test_detail(test_name, out_dir / f"wallsign_negfixed_{test_name}_detail_{args.split}.png", args.split)


if __name__ == "__main__":
    main()