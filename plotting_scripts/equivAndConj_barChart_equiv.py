import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validation F1 (%), transcribed from tab:equivAndConj_equivalences.
data = {
    "Hotel / WallSign": {
        "DSL":  {0.8: {"building": 11.25, "concept": 11.25}, 0.5: {"building": 22.50, "concept": 22.50}},
        "Wide": {0.8: {"building": 36.51, "concept": 36.50}, 0.5: {"building": 0.00,  "concept": 0.00}},
    },
    "Store / Billboard": {
        "DSL":  {0.8: {"building": 25.96, "concept": 25.96}, 0.5: {"building": 49.33, "concept": 49.40}},
        "Wide": {0.8: {"building": 11.60, "concept": 11.60}, 0.5: {"building": 25.99, "concept": 25.99}},
    },
    "ConstructionSite / Machine": {
        "DSL":  {0.8: {"building": 43.67, "concept": 43.68}, 0.5: {"building": 5.77,  "concept": 5.77}},
        "Wide": {0.8: {"building": 0.00,  "concept": 0.00},  0.5: {"building": 29.12, "concept": 29.12}},
    },
    "Suburban / Porch": {
        "DSL":  {0.8: {"building": 12.27, "concept": 12.27}, 0.5: {"building": 53.52, "concept": 53.51}},
        "Wide": {0.8: {"building": 26.80, "concept": 26.79}, 0.5: {"building": 0.00,  "concept": 0.00}},
    },
}

architectures = ["DSL", "Wide"]
alphas = [0.8, 0.5]
bar_keys = ["building", "concept"]
bar_labels = ["Building", "Concept"]
bar_colors = ["#1f77b4", "#ff7f0e"]


def main():
    parser = argparse.ArgumentParser(description="Bar chart of equivalence-axiom building/concept F1.")
    parser.add_argument("--group-by", choices=["architecture", "alpha"], default="architecture")
    parser.add_argument("--out", default="equivAndConj_equivalences_bar_chart.png")
    args = parser.parse_args()

    if args.group_by == "architecture":
        combos = [(arch, alpha) for arch in architectures for alpha in alphas]
        x_group_labels = [f"{arch}\nα={alpha}" for arch, alpha in combos]
    else:
        combos = [(arch, alpha) for alpha in alphas for arch in architectures]
        x_group_labels = [f"α={alpha}\n{arch}" for arch, alpha in combos]

    x = np.arange(len(x_group_labels))
    bar_width = 0.35

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()

    for ax, (pair_name, pair_data) in zip(axes, data.items()):
        for bi, key in enumerate(bar_keys):
            heights = [pair_data[arch][alpha][key] for arch, alpha in combos]
            offset = (bi - 0.5) * bar_width
            ax.bar(x + offset, heights, bar_width, label=bar_labels[bi], color=bar_colors[bi])
        ax.set_xticks(x)
        ax.set_xticklabels(x_group_labels)
        ax.set_ylabel("Validation F1 (%)")
        ax.set_title(pair_name)
        ax.set_ylim(0, 100)
        ax.grid(True, axis="y", alpha=0.3)

    axes[0].legend(loc="upper right", fontsize=9)
    fig.suptitle("Equivalence Axioms: Building vs. Concept F1 (Validation)")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()