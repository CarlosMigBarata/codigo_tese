import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validation F1 (%), transcribed directly from the LaTeX table.
data = {
    "Hotel / WallSign": {
        "DSL":  {0.8: {"baseline": 21.02, "building": 36.48, "concept": 36.46},
                 0.5: {"baseline": 0.00,  "building": 11.25, "concept": 11.25}},
        "Wide": {0.8: {"baseline": 25.61, "building": 25.29, "concept": 25.29},
                 0.5: {"baseline": 25.26, "building": 11.25, "concept": 11.25}},
    },
    "Store / Billboard": {
        "DSL":  {0.8: {"baseline": 25.92, "building": 0.00,  "concept": 0.00},
                 0.5: {"baseline": 0.00,  "building": 37.52, "concept": 37.52}},
        "Wide": {0.8: {"baseline": 53.71, "building": 52.03, "concept": 52.03},
                 0.5: {"baseline": 0.00,  "building": 37.82, "concept": 37.81}},
    },
    "Suburban / Porch": {
        "DSL":  {0.8: {"baseline": 53.82, "building": 26.79, "concept": 26.79},
                 0.5: {"baseline": 0.00,  "building": 53.73, "concept": 53.75}},
        "Wide": {0.8: {"baseline": 26.79, "building": 0.00,  "concept": 0.00},
                 0.5: {"baseline": 53.57, "building": 0.00,  "concept": 0.00}},
    },
    "ConstructionSite / Machine": {
        "DSL":  {0.8: {"baseline": 29.19, "building": 29.23, "concept": 29.21},
                 0.5: {"baseline": 0.00,  "building": 29.07, "concept": 29.06}},
        "Wide": {0.8: {"baseline": 30.58, "building": 29.14, "concept": 29.15},
                 0.5: {"baseline": 0.00,  "building": 14.59, "concept": 14.59}},
    },
}

architectures = ["DSL", "Wide"]
alphas = [0.8, 0.5]
bar_keys = ["baseline", "building", "concept"]
bar_labels = ["Baseline", "Building", "Concept"]
bar_colors = ["#999999", "#1f77b4", "#ff7f0e"]


def main():
    parser = argparse.ArgumentParser(
        description="Bar chart of equivalence-linked building/concept F1 vs. baseline."
    )
    parser.add_argument("--group-by", choices=["architecture", "alpha"], default="architecture",
                         help="Outer x-axis grouping: 'architecture' gives [DSL α0.8, DSL α0.5, "
                              "Wide α0.8, Wide α0.5] (default); 'alpha' gives [α0.8 DSL, α0.8 Wide, "
                              "α0.5 DSL, α0.5 Wide] so same-alpha bars sit next to each other.")
    parser.add_argument("--out", default="equivalence_pairs_bar_chart.png")
    args = parser.parse_args()

    if args.group_by == "architecture":
        combos = [(arch, alpha) for arch in architectures for alpha in alphas]
        x_group_labels = [f"{arch}\nα={alpha}" for arch, alpha in combos]
    else:
        combos = [(arch, alpha) for alpha in alphas for arch in architectures]
        x_group_labels = [f"α={alpha}\n{arch}" for arch, alpha in combos]

    x = np.arange(len(x_group_labels))
    bar_width = 0.25

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()

    for ax, (pair_name, pair_data) in zip(axes, data.items()):
        for bi, key in enumerate(bar_keys):
            heights = [pair_data[arch][alpha][key] for arch, alpha in combos]
            offset = (bi - 1) * bar_width
            ax.bar(x + offset, heights, bar_width, label=bar_labels[bi], color=bar_colors[bi])
        ax.set_xticks(x)
        ax.set_xticklabels(x_group_labels)
        ax.set_ylabel("Validation F1 (%)")
        ax.set_title(pair_name)
        ax.set_ylim(0, 100)
        ax.grid(True, axis="y", alpha=0.3)

    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("Equivalence-Linked Pairs: Baseline vs. Axiom-Trained F1 (Validation)")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()