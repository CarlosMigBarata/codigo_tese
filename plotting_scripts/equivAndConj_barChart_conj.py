import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validation F1 (%), transcribed from tab:equivAndConj_rest.
data = {
    "MiscCommercial ≡ Awning ∧ Table": {
        "concept_labels": ("Awning", "Table"),
        "DSL":  {0.8: {"building": 0.00, "c1": 23.16, "c2": 18.61}, 0.5: {"building": 0.00, "c1": 16.41, "c2": 13.00}},
        "Wide": {0.8: {"building": 0.00, "c1": 0.00,  "c2": 25.05}, 0.5: {"building": 0.00, "c1": 11.61, "c2": 0.70}},
    },
    "PowerPlant ≡ Chimney ∧ Pipe": {
        "concept_labels": ("Chimney", "Pipe"),
        "DSL":  {0.8: {"building": 0.00, "c1": 28.97, "c2": 0.00},  0.5: {"building": 9.76, "c1": 35.21, "c2": 15.63}},
        "Wide": {0.8: {"building": 0.00, "c1": 0.45,  "c2": 25.45}, 0.5: {"building": 0.00, "c1": 23.47, "c2": 5.32}},
    },
    "WaterTreatment ≡ Pipe ∧ Truck": {
        "concept_labels": ("Pipe", "Truck"),
        "DSL":  {0.8: {"building": 0.00, "c1": 0.00,  "c2": 42.96}, 0.5: {"building": 8.15, "c1": 15.63, "c2": 50.69}},
        "Wide": {0.8: {"building": 0.00, "c1": 25.45, "c2": 36.72}, 0.5: {"building": 0.00, "c1": 5.32,  "c2": 31.49}},
    },
    "CountryHouse ≡ Car ∧ TiledRoof": {
        "concept_labels": ("Car", "TiledRoof"),
        "DSL":  {0.8: {"building": 8.10, "c1": 23.92, "c2": 16.70}, 0.5: {"building": 0.00, "c1": 27.94, "c2": 22.28}},
        "Wide": {0.8: {"building": 0.00, "c1": 14.93, "c2": 0.00},  0.5: {"building": 0.00, "c1": 15.71, "c2": 24.25}},
    },
}

architectures = ["DSL", "Wide"]
alphas = [0.8, 0.5]
bar_keys = ["building", "c1", "c2"]
bar_colors = ["#999999", "#1f77b4", "#ff7f0e"]


def main():
    parser = argparse.ArgumentParser(description="Bar chart of conjunction-axiom building/concept F1.")
    parser.add_argument("--group-by", choices=["architecture", "alpha"], default="architecture")
    parser.add_argument("--out", default="equivAndConj_conjunctions_bar_chart.png")
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

    for ax, (group_name, group_data) in zip(axes, data.items()):
        c1_name, c2_name = group_data["concept_labels"]
        bar_labels = ["Building", c1_name, c2_name]
        for bi, key in enumerate(bar_keys):
            heights = [group_data[arch][alpha][key] for arch, alpha in combos]
            offset = (bi - 1) * bar_width
            ax.bar(x + offset, heights, bar_width, label=bar_labels[bi], color=bar_colors[bi])
        ax.set_xticks(x)
        ax.set_xticklabels(x_group_labels)
        ax.set_ylabel("Validation F1 (%)")
        ax.set_title(group_name)
        ax.set_ylim(0, 100)
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Conjunction Axioms: Building vs. Concept F1 (Validation)")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()