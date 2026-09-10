import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

SATISFACTION_COLOR = "#3ed62a"
CLASSIFICATION_COLOR = "#2a78d6"
COMBINED_COLOR = "#e34948"


def find_metrics_files(root: Path):
    if (root / "metrics.csv").exists():
        return [root / "metrics.csv"]
    return sorted(root.glob("**/metrics.csv"))


def load_metrics(path: Path):
    rows = list(csv.DictReader(open(path)))
    epochs = [int(r["Epoch"]) for r in rows]
    train_loss = [float(r["train_loss"]) for r in rows]
    val_loss = [float(r["val_loss"]) for r in rows]
    sat_train_loss = [(1 - float(r["train_sat_kb"])) for r in rows]
    sat_val_loss = [(1 - float(r["train_sat_kb"])) for r in rows]
    combined_train = [float(r["combined_train_loss"]) for r in rows]
    combined_val = [float(r["combined_val_loss"]) for r in rows]
    alpha = rows[0].get("alpha") or rows[0].get("Alpha") if rows else None
    return epochs, train_loss, val_loss, sat_train_loss, sat_val_loss, combined_train, combined_val, alpha


def make_plot(epochs, classification, satisfaction, combined, title, out_path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(epochs, classification, label="Classification loss", color=CLASSIFICATION_COLOR)
    ax.plot(epochs, satisfaction, label="Satisfaction loss", color=SATISFACTION_COLOR)
    ax.plot(epochs, combined, label="Combined loss", color=COMBINED_COLOR)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_run(metrics_path: Path, out_dir: Path = None):
    epochs, train_loss, val_loss, sat_train, sat_val, combined_train, combined_val, alpha = load_metrics(metrics_path)
    run_dir = metrics_path.parent
    run_name = run_dir.name
    dest = out_dir if out_dir is not None else run_dir
    dest.mkdir(parents=True, exist_ok=True)

    suffix = f" (alpha={alpha})" if alpha is not None else ""

    make_plot(epochs, train_loss, sat_train, combined_train,
              f"{run_name} - Train{suffix}", dest / f"{run_name}_loss_train.png")
    make_plot(epochs, val_loss, sat_val, combined_val,
              f"{run_name} - Validation{suffix}", dest / f"{run_name}_loss_val.png")

    print(f"{run_name}: saved loss_train.png and loss_val.png in {dest}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot classification and combined loss per epoch, for every run found under a folder."
    )
    parser.add_argument(
        "folder",
        help="A single run folder (containing metrics.csv directly), or a parent "
             "folder containing multiple run*_outputs subfolders.",
    )
    parser.add_argument(
        "--outdir",
        default=None,
        help="Optional: save all plots here instead of alongside each run's own metrics.csv.",
    )
    args = parser.parse_args()

    root = Path(args.folder)
    metrics_files = find_metrics_files(root)

    if not metrics_files:
        print(f"No metrics.csv found under {root}")
        return

    out_dir = Path(args.outdir) if args.outdir else None
    for path in metrics_files:
        try:
            plot_run(path, out_dir)
        except (KeyError, ValueError) as e:
            print(f"Skipping {path} (unexpected format: {e})")


if __name__ == "__main__":
    main()