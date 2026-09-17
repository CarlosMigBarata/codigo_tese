import argparse
import re
import statistics
from collections import defaultdict
from pathlib import Path


#USAGE: python3 compile_building_label_f1.py path/to/testRun_folder --with-std --by-alpha

# Toggle "active" to control which building labels are included in the table.
# BUILDING_CLASSES = {
#     "Cafe":             {"active": False},
#     "Hotel":            {"active": False},
#     "Restaurant":       {"active": False},
#     "Store":            {"active": False},
#     "MiscCommercial":   {"active": False},
#     "Suburban":         {"active": False},
#     "MiscResidential":  {"active": False},
#     "CountryHouse":     {"active": False},
#     "ConstructionSite": {"active": False},
#     "MiscIndustrial":   {"active": False},
#     "PowerPlant":       {"active": False},
#     "WaterTreatment":   {"active": False},
# }

# # Toggle "active" to control which concepts are included in the table.
# CONCEPTS = {
#     "Door":           {"active": False},
#     "Window":         {"active": False},
#     "Awning":         {"active": False},
#     "Billboard":      {"active": False},
#     "Porch":          {"active": False},
#     "Sign":           {"active": False},
#     "Table":          {"active": False},
#     "TiledRoof":      {"active": False},
#     "TiledRoofTop":   {"active": False},
#     "VendingMachine": {"active": False},
#     "WallSign":       {"active": False},
#     "Statue":         {"active": False},
#     "Chimney":        {"active": False},
#     "Pipe":           {"active": False},
#     "Machine":        {"active": False},
#     "Truck":          {"active": False},
#     "Car":            {"active": False},
# }

BUILDING_CLASSES = {
    "Cafe":             {"active": False},
    "Hotel":            {"active": True},
    "Restaurant":       {"active": False},
    "Store":            {"active": True},
    "MiscCommercial":   {"active": False},
    "Suburban":         {"active": True},
    "MiscResidential":  {"active": False},
    "CountryHouse":     {"active": False},
    "ConstructionSite": {"active": True},
    "MiscIndustrial":   {"active": False},
    "PowerPlant":       {"active": False},
    "WaterTreatment":   {"active": False},
}

# Toggle "active" to control which concepts are included in the table.
CONCEPTS = {
    "Door":           {"active": False},
    "Window":         {"active": False},
    "Awning":         {"active": False},
    "Billboard":      {"active": True},
    "Porch":          {"active": True},
    "Sign":           {"active": False},
    "Table":          {"active": False},
    "TiledRoof":      {"active": False},
    "TiledRoofTop":   {"active": False},
    "VendingMachine": {"active": False},
    "WallSign":       {"active": True},
    "Statue":         {"active": False},
    "Chimney":        {"active": False},
    "Pipe":           {"active": False},
    "Machine":        {"active": True},
    "Truck":          {"active": False},
    "Car":            {"active": False},
}


BLOCK_RE = re.compile(r"(\w+)_(train|val) confusion matrix:.*?f1:\s*([\d.]+)%", re.DOTALL)
HIGH_BIAS_MARKER = "HIGH BIAS METRICS"
ALPHA_RE = re.compile(r"Alpha:\s*([\d.]+)")


def parse_conf_matrix(path: Path):
    text = path.read_text()
    if HIGH_BIAS_MARKER in text:
        text = text.split(HIGH_BIAS_MARKER)[0]
    return BLOCK_RE.findall(text)


def get_alpha(run_dir: Path):
    best_file = run_dir / "best_epoch_results.txt"
    if not best_file.exists():
        return None
    m = ALPHA_RE.search(best_file.read_text())
    return float(m.group(1)) if m else None


def find_conf_matrix_files(root: Path):
    if root.is_file():
        return [root]
    if (root / "conf_matrix.txt").exists():
        return [root / "conf_matrix.txt"]
    return sorted(root.glob("run*_outputs/conf_matrix.txt"))


def collect_f1(root: Path, active_classes, by_alpha: bool):
    # groups[key][class][split] = [f1, ...]; key is an alpha float, or "all" when not splitting
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    files = find_conf_matrix_files(root)
    for f in files:
        key = "all"
        if by_alpha:
            key = get_alpha(f.parent)
            if key is None:
                print(f"Skipping {f} (no alpha found in best_epoch_results.txt)")
                continue
        for name, split, f1 in parse_conf_matrix(f):
            if name in active_classes:
                groups[key][name][split].append(float(f1))
    return groups, files


def mean_std(values):
    if not values:
        return None, None
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0.0
    return m, s


def format_cell(values, with_std):
    m, s = mean_std(values)
    if m is None:
        return "-"
    if with_std:
        return f"${m:.2f} \\pm {s:.2f}$"
    return f"{m:.2f}"


def print_latex_table(values, active_classes, row_label, caption, label, with_std):
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\begin{tabular}{lcc}",
        r"\hline",
        f"\\textbf{{{row_label}}} & \\textbf{{Train F1 (\\%)}} & \\textbf{{Val F1 (\\%)}} \\\\",
        r"\hline",
    ]
    for name in active_classes:
        train_s = format_cell(values[name]["train"], with_std)
        val_s = format_cell(values[name]["val"], with_std)
        lines.append(f"{name} (Wide Baseline) & {train_s} & {val_s} \\\\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        r"\end{table}",
    ]
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Average F1 per building label and per concept across the runs in a "
                    "testRun folder, printed as LaTeX tables. Edit BUILDING_CLASSES / "
                    "CONCEPTS at the top of this file to toggle which are included."
    )
    parser.add_argument("path", help="A testRun folder (containing run*_outputs), a single "
                                      "run folder, or a conf_matrix.txt file.")
    parser.add_argument("--by-alpha", action="store_true",
                         help="Print a separate pair of tables per alpha value, instead of "
                              "averaging all runs together.")
    parser.add_argument("--with-std", action="store_true",
                         help="Print mean +/- standard deviation instead of just the mean.")
    args = parser.parse_args()

    root = Path(args.path)
    active_buildings = [name for name, cfg in BUILDING_CLASSES.items() if cfg["active"]]
    active_concepts = [name for name, cfg in CONCEPTS.items() if cfg["active"]]
    all_active = active_buildings + active_concepts

    groups, files = collect_f1(root, all_active, args.by_alpha)

    if not files:
        print(f"No conf_matrix.txt found under {root}")
        return
    print(f"Found {len(files)} run(s) under {root}\n")

    keys = sorted(groups.keys(), reverse=True) if args.by_alpha else ["all"]

    for key in keys:
        values = groups[key]
        suffix = f"_alpha{key:g}" if args.by_alpha else ""
        alpha_note = f" (alpha={key:g})" if args.by_alpha else ""

        if args.by_alpha:
            print(f"=== alpha = {key:g} ===")

        if active_buildings and any(values[c]["train"] or values[c]["val"] for c in active_buildings):
            print_latex_table(values, active_buildings, "Building Label",
                               f"Average F1 per building label across runs, train and validation{alpha_note}.",
                               f"tab:building_labels_f1{suffix}", args.with_std)
            print()
        else:
            print("No matching building-label data found.\n")

        if active_concepts and any(values[c]["train"] or values[c]["val"] for c in active_concepts):
            print_latex_table(values, active_concepts, "Concept",
                               f"Average F1 per concept across runs, train and validation{alpha_note}.",
                               f"tab:concepts_f1{suffix}", args.with_std)
            print()
        else:
            print("No matching concept data found.\n")


if __name__ == "__main__":
    main()
