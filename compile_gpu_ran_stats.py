import argparse
import csv
import re
import statistics
from pathlib import Path

#usage: python3 compile_gpu_runs_stats.py path/to/outputs --csv results.csv --latex table.txt

FIELD_PATTERNS = {
    "alpha": r"Alpha:\s*([\d.]+)",
    "cls_train": r"Classification Train Loss:\s*([\d.]+)",
    "cls_val": r"Classification Val Loss:\s*([\d.]+)",
    "comb_train": r"Combined Train Loss:\s*([\d.]+)",
    "comb_val": r"Combined Val Loss:\s*([\d.]+)",
    "sat_train_loss": r"Train SAT \(Loss\):\s*([\d.]+)",
    "sat_val_loss": r"Val SAT \(Loss\):\s*([\d.]+)",
}

METRIC_LABELS = [
    ("sat_train", "sat_val", "Satisfaction KB"),
    ("cls_train", "cls_val", "Classification Loss"),
    ("comb_train", "comb_val", "Combined Loss"),
]


def parse_best_epoch(path: Path):
    text = path.read_text()
    values = {}
    for key, pattern in FIELD_PATTERNS.items():
        m = re.search(pattern, text)
        values[key] = float(m.group(1)) if m else None
    return values


def collect_run_values(test_run_dir: Path):
    by_alpha = {}
    for run_dir in sorted(test_run_dir.glob("run*_outputs")):
        best_file = run_dir / "best_epoch_results.txt"
        if not (run_dir / "DONE").exists() or not best_file.exists():
            print(f"Skipping {run_dir} (incomplete)")
            continue
        values = parse_best_epoch(best_file)
        if any(v is None for v in values.values()):
            print(f"Skipping {run_dir} (missing fields in best_epoch_results.txt)")
            continue
        values["sat_train"] = 1 - values["sat_train_loss"]
        values["sat_val"] = 1 - values["sat_val_loss"]
        by_alpha.setdefault(values["alpha"], []).append(values)
    return by_alpha


def mean_std(values):
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0.0
    return m, s


def summarize(rows):
    keys = ["cls_train", "cls_val", "comb_train", "comb_val", "sat_train", "sat_val"]
    return {k: mean_std([r[k] for r in rows]) for k in keys}


def pretty_name(folder_name: str):
    name = folder_name
    for prefix in ("testRun_only", "testRun_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    name = name.replace("_GPU", "").replace("_", " ")
    name = re.sub(r"(?<!^)(?=[A-Z])", " ", name).strip()
    return name


def print_table(summaries):
    header = f"{'Config':22}{'Alpha':>7}{'N':>3}  " + "  ".join(
        f"{label + ' (Train)':>22}{label + ' (Val)':>22}" for _, _, label in METRIC_LABELS
    )
    print(header)
    for name, alpha, n, summary in summaries:
        cells = []
        for train_key, val_key, _ in METRIC_LABELS:
            tm, ts = summary[train_key]
            vm, vs = summary[val_key]
            cells.append(f"{tm:.4f}+-{ts:.4f}".rjust(22) + f"{vm:.4f}+-{vs:.4f}".rjust(22))
        print(f"{name:22}{alpha:>7.2f}{n:>3}  " + "  ".join(cells))


def write_csv(summaries, out_path):
    fieldnames = ["config", "alpha", "n"]
    for train_key, val_key, _ in METRIC_LABELS:
        fieldnames += [f"{train_key}_mean", f"{train_key}_std", f"{val_key}_mean", f"{val_key}_std"]
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for name, alpha, n, summary in summaries:
            row = {"config": name, "alpha": alpha, "n": n}
            for train_key, val_key, _ in METRIC_LABELS:
                tm, ts = summary[train_key]
                vm, vs = summary[val_key]
                row[f"{train_key}_mean"] = tm
                row[f"{train_key}_std"] = ts
                row[f"{val_key}_mean"] = vm
                row[f"{val_key}_std"] = vs
            writer.writerow(row)
    print(f"\nWrote {out_path}")


def write_latex(summaries, out_path):
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{ll" + "cc" * len(METRIC_LABELS) + "}")
    lines.append(r"\hline")
    header1 = " & & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{\\textbf{{{label}}}}}" for _, _, label in METRIC_LABELS
    ) + r" \\"
    lines.append(header1)
    header2 = "Config & $\\alpha$ & " + " & ".join("Train & Val" for _ in METRIC_LABELS) + r" \\"
    lines.append(header2)
    lines.append(r"\hline")
    for name, alpha, n, summary in summaries:
        cells = [name, f"{alpha:g}"]
        for train_key, val_key, _ in METRIC_LABELS:
            tm, ts = summary[train_key]
            vm, vs = summary[val_key]
            cells.append(f"${tm:.4f} \\pm {ts:.4f}$")
            cells.append(f"${vm:.4f} \\pm {vs:.4f}$")
        lines.append(" & ".join(cells) + r" \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{Mean $\pm$ standard deviation across repeated seeds, at best epoch.}")
    lines.append(r"\label{tab:gpu_runs_stats}")
    lines.append(r"\end{table}")

    content = "\n".join(lines)
    if out_path:
        Path(out_path).write_text(content)
        print(f"Wrote {out_path}")
    else:
        print("\n" + content)


def main():
    parser = argparse.ArgumentParser(
        description="For each testRun_only*_GPU folder, compute mean/std of classification "
                    "loss, satisfaction and combined loss (train+val) across its runs, at each "
                    "run's best epoch."
    )
    parser.add_argument("path", help="Folder containing testRun_only*_GPU subfolders "
                                      "(e.g. the 'outputs' directory).")
    parser.add_argument("--csv", default=None, help="Optional: write a summary CSV here.")
    parser.add_argument("--latex", default=None, help="Optional: write the LaTeX table to this file "
                                                        "instead of printing it.")
    args = parser.parse_args()

    root = Path(args.path)
    test_run_dirs = sorted(root.glob("testRun_only*_GPU"))
    if not test_run_dirs:
        print(f"No testRun_only*_GPU folders found under {root}")
        return

    summaries = []
    for test_run_dir in test_run_dirs:
        by_alpha = collect_run_values(test_run_dir)
        if not by_alpha:
            print(f"No usable runs in {test_run_dir}, skipping")
            continue
        for alpha in sorted(by_alpha, reverse=True):
            rows = by_alpha[alpha]
            summary = summarize(rows)
            summaries.append((pretty_name(test_run_dir.name), alpha, len(rows), summary))

    print_table(summaries)

    if args.csv:
        write_csv(summaries, args.csv)

    write_latex(summaries, args.latex)


if __name__ == "__main__":
    main()
