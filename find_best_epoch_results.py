import re
import sys
from pathlib import Path

import pandas as pd

EPOCH_RE = re.compile(r"Epoch (\d+)")


def find_best_epoch(run_dir: Path):
    best_file = run_dir / "best_epoch_results.txt"
    if not best_file.exists():
        return None
    m = EPOCH_RE.search(best_file.read_text())
    return int(m.group(1)) if m else None


def get_latex_line(run_dir: Path, best_epoch: int):
    metrics_path = run_dir / "metrics.csv"
    df = pd.read_csv(metrics_path)
    matches = df[df["Epoch"] == best_epoch]

    alpha = float(matches["Alpha"].item())

    train_sat_kb = float(matches["train_sat_kb"].item())
    val_sat_kb = float(matches["val_sat_kb"].item())

    train_class_loss = float(matches["train_loss"].item())
    val_class_loss = float(matches["val_loss"].item())

    train_combined_loss = float(matches["combined_train_loss"].item())
    val_combined_loss = float(matches["combined_val_loss"].item())

    line = (f"{alpha:.2f} (DSL) & {train_sat_kb:.4f} & {val_sat_kb:.4f} & "
            f"{train_class_loss:.4f} & {val_class_loss:.4f} & "
            f"{train_combined_loss:.4f} & {val_combined_loss:.4f} \\\\")
    return alpha, line


def find_run_dirs(root: Path):
    if (root / "metrics.csv").exists():
        return [root]
    return sorted(root.glob("run*_outputs"))


def main():
    if len(sys.argv) < 2:
        print("USAGE: python3 find_best_epoch_results.py path/to/dir")
        return

    input_dir = Path(sys.argv[1])
    run_dirs = find_run_dirs(input_dir)

    if not run_dirs:
        print(f"No run*_outputs (or metrics.csv) found under {input_dir}")
        return

    results = []
    for run_dir in run_dirs:
        best_epoch = find_best_epoch(run_dir)
        if best_epoch is None:
            print(f"{run_dir.name}: no best_epoch_results.txt found, skipping")
            continue
        try:
            alpha, line = get_latex_line(run_dir, best_epoch)
        except Exception as e:
            print(f"{run_dir.name}: could not read metrics.csv for epoch {best_epoch} ({e})")
            continue
        results.append((alpha, run_dir, best_epoch, line))

    results.sort(key=lambda r: r[0], reverse=True)

    for alpha, run_dir, best_epoch, line in results:
        #print(f"{run_dir.name} (epoch {best_epoch}):")
        print(line)
        #print()


if __name__ == "__main__":
    main()
