#usage: 
# python3 compile_f1_scores.py path/to/testRun_folder --outdir path/to/save/plots --csv results.csv



import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

SUPER_CLASSES = ["Residential", "Commercial", "Industrial"]
BUILDING_LABELS = [
    "Cafe", "Hotel", "Restaurant", "Store", "MiscCommercial", "Suburban",
    "MiscResidential", "CountryHouse", "ConstructionSite", "MiscIndustrial",
    "PowerPlant", "WaterTreatment",
]
CONCEPTS = [
    "Door", "Window", "Awning", "Billboard", "Porch", "Sign", "Table",
    "TiledRoof", "TiledRoofTop", "VendingMachine", "WallSign", "Statue",
    "Chimney", "Pipe", "Machine", "Truck", "Car",
]

GROUP_OF = {}
for name in SUPER_CLASSES:
    GROUP_OF[name] = "super_classes"
for name in BUILDING_LABELS:
    GROUP_OF[name] = "building_labels"
for name in CONCEPTS:
    GROUP_OF[name] = "concepts"

GROUP_ORDER = ["all", "super_classes", "building_labels", "concepts"]
GROUP_COLORS = {
    "all": "#444444",
    "super_classes": "#2a78d6",
    "building_labels": "#e34948",
    "concepts": "#2ca02c",
}

BLOCK_RE = re.compile(r"(\w+)_(train|val) confusion matrix:.*?f1:\s*([\d.]+)%", re.DOTALL)
HIGH_BIAS_MARKER = "HIGH BIAS METRICS"
ALPHA_RE = re.compile(r"Alpha:\s*([\d.]+)")


def parse_conf_matrix(path: Path):
    text = path.read_text()
    if HIGH_BIAS_MARKER in text:
        text = text.split(HIGH_BIAS_MARKER)[0]

    entries = []
    unknown = set()
    for name, split, f1 in BLOCK_RE.findall(text):
        group = GROUP_OF.get(name)
        if group is None:
            unknown.add(name)
            continue
        entries.append((name, split, group, float(f1)))
    return entries, unknown


def parse_alpha(run_dir: Path):
    best_file = run_dir / "best_epoch_results.txt"
    if not best_file.exists():
        return None
    m = ALPHA_RE.search(best_file.read_text())
    return float(m.group(1)) if m else None


def summarize(entries):
    buckets = defaultdict(list)
    for name, split, group, f1 in entries:
        buckets[(split, "all")].append(f1)
        buckets[(split, group)].append(f1)

    result = {}
    for split in ("train", "val"):
        result[split] = {}
        for group in GROUP_ORDER:
            values = buckets.get((split, group), [])
            result[split][group] = (sum(values) / len(values)) if values else None
    return result


def print_summary(path: Path, alpha, summary):
    alpha_s = f"{alpha:g}" if alpha is not None else "?"
    print(f"\n{path} (alpha={alpha_s})")
    print(f"{'':16}{'Train':>10}{'Val':>10}")
    for group in GROUP_ORDER:
        train_v = summary["train"][group]
        val_v = summary["val"][group]
        train_s = f"{train_v:.3f}" if train_v is not None else "-"
        val_s = f"{val_v:.3f}" if val_v is not None else "-"
        print(f"{group:16}{train_s:>10}{val_s:>10}")


def find_conf_matrix_files(root: Path):
    if root.is_file():
        return [root]
    if (root / "conf_matrix.txt").exists():
        return [root / "conf_matrix.txt"]
    return sorted(root.glob("**/conf_matrix.txt"))


def make_plot(runs, split, title, out_path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for group in GROUP_ORDER:
        alphas = [r["alpha"] for r in runs]
        values = [r["summary"][split][group] for r in runs]
        ax.plot(alphas, values, marker="o", label=group, color=GROUP_COLORS[group])
    ax.set_xlabel("Alpha")
    ax.set_ylabel("F1 (%)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Average F1 (overall, super-classes, building classes, concepts) "
                    "per train/val split, from one or more conf_matrix.txt files, "
                    "plotted against each run's alpha (read from best_epoch_results.txt)."
    )
    parser.add_argument("path", help="A conf_matrix.txt file, a single run folder, or a parent folder.")
    parser.add_argument("--csv", default=None, help="Optional: write a combined CSV of all results here.")
    parser.add_argument("--outdir", default=None,
                         help="Where to save the train/val F1-vs-alpha plots. Defaults to the input folder.")
    args = parser.parse_args()

    root = Path(args.path)
    files = find_conf_matrix_files(root)
    if not files:
        print(f"No conf_matrix.txt found under {root}")
        return

    runs = []
    for f in files:
        entries, unknown = parse_conf_matrix(f)
        if unknown:
            print(f"Note: {f} has classes not in the known ontology (skipped): {sorted(unknown)}")
        alpha = parse_alpha(f.parent)
        if alpha is None:
            print(f"Skipping {f} (no alpha found in best_epoch_results.txt)")
            continue
        summary = summarize(entries)
        runs.append({"path": f, "alpha": alpha, "summary": summary})

    runs.sort(key=lambda r: r["alpha"])

    csv_rows = []
    for r in runs:
        print_summary(r["path"], r["alpha"], r["summary"])
        for split in ("train", "val"):
            row = {"run": str(r["path"].parent), "alpha": r["alpha"], "split": split}
            row.update({g: r["summary"][split][g] for g in GROUP_ORDER})
            csv_rows.append(row)

    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["run", "alpha", "split"] + GROUP_ORDER)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\nWrote {args.csv}")

    if not runs:
        return

    out_dir = Path(args.outdir) if args.outdir else root
    out_dir.mkdir(parents=True, exist_ok=True)
    make_plot(runs, "train", "F1 vs Alpha - Train", out_dir / "f1_vs_alpha_train.png")
    make_plot(runs, "val", "F1 vs Alpha - Validation", out_dir / "f1_vs_alpha_val.png")


if __name__ == "__main__":
    main()


#usage: python3 compile_f1_scores.py path/to/testRun_folder --outdir path/to/save/plots --csv results.csv