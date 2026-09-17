import argparse
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path


#USAGE: python3 compile_building_label_f1.py path/to/testRun_folder --with-std --by-alpha --metric mcc

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

# # Toggle "active" to control which concepts are included in the table.
CONCEPTS = {
    "Door":           {"active": False},
    "Window":         {"active": False},
    "Awning":         {"active": True},
    "Billboard":      {"active": False},
    "Porch":          {"active": True},
    "Sign":           {"active": False},
    "Table":          {"active": True},
    "TiledRoof":      {"active": True},
    "TiledRoofTop":   {"active": False},
    "VendingMachine": {"active": False},
    "WallSign":       {"active": False},
    "Statue":         {"active": False},
    "Chimney":        {"active": True},
    "Pipe":           {"active": True},
    "Machine":        {"active": False},
    "Truck":          {"active": False},
    "Car":            {"active": True},
}


BUILDING_CLASSES = {
    "Cafe":             {"active": True},
    "Hotel":            {"active": True},
    "Restaurant":       {"active": True},
    "Store":            {"active": True},
    "MiscCommercial":   {"active": True},
    "Suburban":         {"active": True},
    "MiscResidential":  {"active": True},
    "CountryHouse":     {"active": True},
    "ConstructionSite": {"active": True},
    "MiscIndustrial":   {"active": True},
    "PowerPlant":       {"active": True},
    "WaterTreatment":   {"active": True},
}

# Toggle "active" to control which concepts are included in the table.


# Matrix is printed as [[TN, FP], [FN, TP]] -- see the "FORMATO DA MATRIZ" header
# at the top of conf_matrix.txt.
BLOCK_RE = re.compile(
    r"(\w+)_(train|val) confusion matrix:\s*"
    r"tensor\(\[\[\s*(\d+),\s*(\d+)\],\s*\[\s*(\d+),\s*(\d+)\]\]"
)
HIGH_BIAS_MARKER = "HIGH BIAS METRICS"
ALPHA_RE = re.compile(r"Alpha:\s*([\d.]+)")


def compute_f1(tp, tn, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_balanced_accuracy(tp, tn, fp, fn):
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return (recall + specificity) / 2


def compute_mcc(tp, tn, fp, fn):
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    if denom == 0:
        return 0.0
    return (tp * tn - fp * fn) / denom


# name -> (function, is_percentage, display_name)
METRICS = {
    "f1":               (compute_f1, True, "F1"),
    "balanced_accuracy": (compute_balanced_accuracy, True, "Balanced Accuracy"),
    "mcc":              (compute_mcc, False, "MCC"),
}


def parse_conf_matrix(path: Path, metric_fn):
    text = path.read_text()
    if HIGH_BIAS_MARKER in text:
        text = text.split(HIGH_BIAS_MARKER)[0]
    results = []
    for name, split, tn, fp, fn, tp in BLOCK_RE.findall(text):
        tn, fp, fn, tp = int(tn), int(fp), int(fn), int(tp)
        results.append((name, split, metric_fn(tp, tn, fp, fn)))
    return results


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


def collect_metric(root: Path, active_classes, by_alpha: bool, metric_fn):
    # groups[key][class][split] = [value, ...]; key is an alpha float, or "all" when not splitting
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    files = find_conf_matrix_files(root)
    for f in files:
        key = "all"
        if by_alpha:
            key = get_alpha(f.parent)
            if key is None:
                print(f"Skipping {f} (no alpha found in best_epoch_results.txt)")
                continue
        for name, split, value in parse_conf_matrix(f, metric_fn):
            if name in active_classes:
                groups[key][name][split].append(value)
    return groups, files


def mean_std(values):
    if not values:
        return None, None
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0.0
    return m, s


def format_cell(values, with_std, as_percent):
    m, s = mean_std(values)
    if m is None:
        return "-"
    scale = 100 if as_percent else 1
    fmt = "{:.2f}" if as_percent else "{:.3f}"
    if with_std:
        return f"${fmt.format(m * scale)} \\pm {fmt.format(s * scale)}$"
    return fmt.format(m * scale)


def print_latex_table(values, active_classes, row_label, caption, label, with_std, as_percent):
    unit = " (\\%)" if as_percent else ""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\begin{tabular}{lcc}",
        r"\hline",
        f"\\textbf{{{row_label}}} & \\textbf{{Train{unit}}} & \\textbf{{Val{unit}}} \\\\",
        r"\hline",
    ]
    for name in active_classes:
        train_s = format_cell(values[name]["train"], with_std, as_percent)
        val_s = format_cell(values[name]["val"], with_std, as_percent)
        lines.append(f"{name} & {train_s} & {val_s} \\\\")
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
        description="Average metric (F1, balanced accuracy or MCC) per building label and per "
                    "concept across the runs in a testRun folder, printed as LaTeX tables. Edit "
                    "BUILDING_CLASSES / CONCEPTS at the top of this file to toggle which are "
                    "included."
    )
    parser.add_argument("path", help="A testRun folder (containing run*_outputs), a single "
                                      "run folder, or a conf_matrix.txt file.")
    parser.add_argument("--metric", choices=sorted(METRICS), default="f1",
                         help="Which metric to report (default: f1). Use 'balanced_accuracy' or "
                              "'mcc' to check whether a collapsed (0.00%% F1) label is stuck at "
                              "0 or actually stuck at 1 -- F1 hides that distinction.")
    parser.add_argument("--by-alpha", action="store_true",
                         help="Print a separate pair of tables per alpha value, instead of "
                              "averaging all runs together.")
    parser.add_argument("--with-std", action="store_true",
                         help="Print mean +/- standard deviation instead of just the mean.")
    args = parser.parse_args()

    root = Path(args.path)
    metric_fn, as_percent, display_name = METRICS[args.metric]
    metric_suffix = "" if args.metric == "f1" else f"_{args.metric}"

    active_buildings = [name for name, cfg in BUILDING_CLASSES.items() if cfg["active"]]
    active_concepts = [name for name, cfg in CONCEPTS.items() if cfg["active"]]
    all_active = active_buildings + active_concepts

    groups, files = collect_metric(root, all_active, args.by_alpha, metric_fn)

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
                               f"Average {display_name} per building label across runs, train and validation{alpha_note}.",
                               f"tab:building_labels{metric_suffix}{suffix}", args.with_std, as_percent)
            print()
        else:
            print("No matching building-label data found.\n")

        if active_concepts and any(values[c]["train"] or values[c]["val"] for c in active_concepts):
            print_latex_table(values, active_concepts, "Concept",
                               f"Average {display_name} per concept across runs, train and validation{alpha_note}.",
                               f"tab:concepts{metric_suffix}{suffix}", args.with_std, as_percent)
            print()
        else:
            print("No matching concept data found.\n")


if __name__ == "__main__":
    main()