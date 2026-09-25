import argparse
import math
import random
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import torchvision.transforms as transforms

import utils.rules_and_concepts as rules_and_concepts
import utils.constants as constants


#USAGE
# Point at a folder containing run*_outputs subfolders; each run's alpha is read
# from its metrics.csv, runs are grouped by alpha, and one set of results is
# printed per alpha group.
# python3 -u random_neuron_baseline.py --root-dir outputs/to_send/to_send_to_GPU_onlyEquiv --trials-per-run 40 --polarity-aware --latex | tee zzz_data_evaluation/output.txt
#
# Old explicit-paths mode still works, for a single combined group:
# python3 random_neuron_baseline.py run0/best_model.pth run1/best_model.pth run2/best_model.pth --trials-per-run 40 --latex

DATA_ROOT = Path("/home/sofia/Desktop/datasets/datasetVCB")

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
SUPER_CLASSES = rules_and_concepts.get_super_classes()
CLASSES = rules_and_concepts.get_all_classes()  # buildings + concepts + super_classes, in this order
super_classes_nbr = len(SUPER_CLASSES)


building_classes = len(ALL_BUILDING_CLASSES)
num_concepts = len(ALL_CONCEPTS)
concepts_pos = num_concepts

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


class BuildingsDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None):
        self.df = dataframe.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image = Image.open(self.img_dir / row["id"]).convert("RGB")
        target = torch.tensor(row[CLASSES].to_numpy(dtype=float), dtype=torch.float32)
        if self.transform:
            image = self.transform(image)
        return image, target


# Same architecture as dissertation_workplace_script_double_sized_layers.py, copied here
# so this script can load a best_model.pth checkpoint without executing that whole
# training script (which expects sys.argv and starts a training run on import).
"""CNN MODEL"""

class CNN(nn.Module):
    def __init__(self, in_channels, num_classes, name="cnn_model"):
        super(CNN, self).__init__()

        nbr_of_neurons = min(len(ALL_CONCEPTS), 48) * 2   # concept layer is doubled
        cnn_num_classes = num_classes                      # buildings are the final output -- not doubled

        self.conv1a = nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3)
        self.conv1b = nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3)
        self.conv2a = nn.Conv2d(in_channels=16, out_channels=16, kernel_size=3)
        self.conv2b = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3)
        self.conv3a = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3)
        self.conv3b = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3)
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3)

        self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.globalAvgPooling = nn.AdaptiveAvgPool2d((1, 1))
        self.flatten = nn.Flatten()
        self.dense1 = nn.Linear(128, 64)

        self.concept_layer = nn.Linear(64, nbr_of_neurons)
        suport_layer1_nbr = math.ceil((nbr_of_neurons + cnn_num_classes) / 2)
        self.suport_layer1 = nn.Linear(nbr_of_neurons, suport_layer1_nbr)
        self.output_layer = nn.Linear(suport_layer1_nbr, cnn_num_classes)

    def forward(self, inputs):
        if isinstance(inputs, (list, tuple)):
            inputs = inputs[0]

        x = F.leaky_relu(self.conv1a(inputs))
        x = F.leaky_relu(self.conv1b(x))
        x = self.maxpool(x)
        x = F.leaky_relu(self.conv2a(x))
        x = self.maxpool(x)
        x = F.leaky_relu(self.conv2b(x))
        x = self.maxpool(x)
        x = F.leaky_relu(self.conv3a(x))
        x = F.leaky_relu(self.conv3b(x))
        x = self.maxpool(x)
        x = F.leaky_relu(self.conv4(x))
        x = self.globalAvgPooling(x)
        x = self.flatten(x)
        x = F.leaky_relu(self.dense1(x))

        concepts = self.concept_layer(x)               # full doubled width (34)
        concepts_activation = F.leaky_relu(concepts)
        x = F.leaky_relu(self.suport_layer1(concepts_activation))
        buildings = self.output_layer(x)                # exactly 12, the final classes

        return buildings, concepts



def load_val_loader(batch_size):
    labels_csv = DATA_ROOT / "all.csv"
    images_dir = DATA_ROOT / "c1"
    df = pd.read_csv(labels_csv, index_col=0)
    df["id"] = df["id"].apply(lambda x: f"{x}.jpg")
    df[CLASSES] = df[CLASSES].apply(pd.to_numeric)

    train_test_limit = int(0.8 * len(df))
    val_df = df[train_test_limit:]

    val_dataset = BuildingsDataset(val_df, images_dir, transform=transform)
    return DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)


def compute_f1(tp, tn, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


@torch.no_grad()
def get_predictions_and_labels(model_path, device, batch_size):
    model = CNN(in_channels=3, num_classes=building_classes).to(device)   # not doubled
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    val_loader = load_val_loader(batch_size)

    all_building_preds, all_concept_preds, all_labels = [], [], []
    for images, targets in val_loader:
        images = images.to(device)
        buildings_out, concepts_out = model(images)

        all_building_preds.append((torch.sigmoid(buildings_out) > 0.5).int().cpu())
        all_concept_preds.append((torch.sigmoid(concepts_out) > 0.5).int().cpu())
        all_labels.append(targets.int())

    return (torch.cat(all_building_preds, dim=0),
            torch.cat(all_concept_preds, dim=0),
            torch.cat(all_labels, dim=0))

def f1_for_index(preds, labels, pred_idx, true_idx, invert=False):
    y_pred = preds[:, pred_idx]
    if invert:
        y_pred = 1 - y_pred
    y_true = labels[:, true_idx]
    tp = int(torch.sum((y_true == 1) & (y_pred == 1)))
    tn = int(torch.sum((y_true == 0) & (y_pred == 0)))
    fp = int(torch.sum((y_true == 0) & (y_pred == 1)))
    fn = int(torch.sum((y_true == 1) & (y_pred == 0)))
    return compute_f1(tp, tn, fp, fn)


def best_polarity_f1(preds, labels, pred_idx, true_idx, polarity_aware):
    """
    Returns (best_f1, polarity) where polarity is "normal" or "inverted".
    If polarity_aware is False, always uses the normal threshold (old behavior).
    """
    normal_f1 = f1_for_index(preds, labels, pred_idx, true_idx, invert=False)
    if not polarity_aware:
        return normal_f1, "normal"
    inverted_f1 = f1_for_index(preds, labels, pred_idx, true_idx, invert=True)
    if inverted_f1 > normal_f1:
        return inverted_f1, "inverted"
    return normal_f1, "normal"


def collect_group_results(pool_preds, group_labels, names, pool_size, trials, rng, polarity_aware):
    """
    designated:          {name: f1}     -- neuron i (i < len(names)) -> label i, normal threshold only
                                            (kept as the plain, non-polarity-aware reference number).
    designated_best:     {name: f1}     -- best_polarity_f1 for the SAME designated neuron.
    designated_polarity: {name: str}    -- "normal" or "inverted", whichever gave designated_best.
    trial_f1s:           {name: [f1,...]} -- one best_polarity_f1 per trial, neuron drawn from the
                                              FULL pool. Uses the SAME polarity_aware convention as
                                              designated_best, so the two are a fair, apples-to-apples
                                              comparison -- otherwise a polarity-aware designated score
                                              would be compared against a polarity-blind random one,
                                              overstating how much better designated looks.
    """
    name_indices = list(range(len(names)))
    designated = {}
    designated_best = {}
    designated_polarity = {}
    for name, idx in zip(names, name_indices):
        designated[name] = f1_for_index(pool_preds, group_labels, idx, idx, invert=False)
        best_f1, polarity = best_polarity_f1(pool_preds, group_labels, idx, idx, polarity_aware)
        designated_best[name] = best_f1
        designated_polarity[name] = polarity

    trial_f1s = {name: [] for name in names}
    pool = list(range(pool_size))
    for _ in range(trials):
        drawn = rng.sample(pool, len(names))
        for name, true_idx, pred_idx in zip(names, name_indices, drawn):
            trial_best_f1, _ = best_polarity_f1(pool_preds, group_labels, pred_idx, true_idx, polarity_aware)
            trial_f1s[name].append(trial_best_f1)

    return designated, designated_best, designated_polarity, trial_f1s


def print_summary_table(names, designated_per_run, designated_best_per_run, polarity_per_run,
                         pooled_trials, group_label, args):
    random_label = "Random mean (best pol.)" if args.polarity_aware else "Random mean"
    random_std_label = "Random std (best pol.)" if args.polarity_aware else "Random std"

    print(f"\n=== {group_label} ===")
    header = f"{'Name':<20} {'Designated (avg)':>17}"
    if args.polarity_aware:
        header += f" {'Best-polarity (avg)':>20} {'Polarity':>10}"
    if not args.designated_only:
        header += f" {random_label:>24} {random_std_label:>23}"
    print(header)
    for name in names:
        avg_designated = statistics.mean(designated_per_run[name])
        line = f"{name:<20} {avg_designated*100:>16.2f}%"
        if args.polarity_aware:
            avg_best = statistics.mean(designated_best_per_run[name])
            polarities = polarity_per_run[name]
            n_inverted = sum(1 for p in polarities if p == "inverted")
            if n_inverted == 0:
                polarity_label = "normal"
            elif n_inverted == len(polarities):
                polarity_label = "inverted"
            else:
                polarity_label = f"mixed ({n_inverted}/{len(polarities)})"
            line += f" {avg_best*100:>19.2f}% {polarity_label:>10}"
        if not args.designated_only:
            pooled = pooled_trials[name]
            mean_f1 = statistics.mean(pooled)
            std_f1 = statistics.stdev(pooled) if len(pooled) > 1 else 0.0
            line += f" {mean_f1*100:>23.2f}% {std_f1*100:>22.2f}%"
        print(line)

    if args.latex:
        print(r"\begin{table}[htbp]")
        print(r"\centering")
        cols = "lc"
        if args.polarity_aware:
            cols += "cc"
        if not args.designated_only:
            cols += "cc"
        print(rf"\begin{{tabular}}{{{cols}}}")
        print(r"\hline")
        header_cells = rf"\textbf{{{group_label}}} & \textbf{{Designated (\%)}}"
        if args.polarity_aware:
            header_cells += r" & \textbf{Best-polarity (\%)} & \textbf{Polarity}"
        if not args.designated_only:
            header_cells += rf" & \textbf{{{random_label} (\%)}} & \textbf{{{random_std_label} (\%)}}"
        print(header_cells + r" \\")
        print(r"\hline")
        for name in names:
            avg_designated = statistics.mean(designated_per_run[name])
            row = f"{name} & {avg_designated*100:.2f}"
            if args.polarity_aware:
                avg_best = statistics.mean(designated_best_per_run[name])
                polarities = polarity_per_run[name]
                n_inverted = sum(1 for p in polarities if p == "inverted")
                if n_inverted == 0:
                    polarity_label = "normal"
                elif n_inverted == len(polarities):
                    polarity_label = "inverted"
                else:
                    polarity_label = f"mixed ({n_inverted}/{len(polarities)})"
                row += f" & {avg_best*100:.2f} & {polarity_label}"
            if not args.designated_only:
                pooled = pooled_trials[name]
                mean_f1 = statistics.mean(pooled)
                std_f1 = statistics.stdev(pooled) if len(pooled) > 1 else 0.0
                row += f" & {mean_f1*100:.2f} & {std_f1*100:.2f}"
            print(row + r" \\")
        print(r"\hline")
        print(r"\end{tabular}")
        print(r"\caption{REPLACE ME}")
        print(rf"\label{{tab:REPLACE_ME_{group_label.lower().replace(' ', '_').replace('(', '').replace(')', '')}}}")
        print(r"\end{table}")


def discover_runs_by_alpha(root_dir):
    """
    Scans root_dir's immediate subdirectories for run folders containing both
    best_model.pth and metrics.csv, reads each run's (constant) alpha from the
    metrics.csv "Alpha" column, and groups run paths by that alpha value.
    Returns: dict {alpha: [Path(best_model.pth), ...]}, sorted by alpha descending.
    """
    root_dir = Path(root_dir)
    groups = {}
    for run_dir in sorted(root_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        model_path = run_dir / "best_model.pth"
        metrics_path = run_dir / "metrics.csv"
        if not model_path.exists():
            continue
        if not metrics_path.exists():
            print(f"[skip] {run_dir.name}: no metrics.csv found")
            continue
        df = pd.read_csv(metrics_path, usecols=["Alpha"])
        if df.empty:
            print(f"[skip] {run_dir.name}: metrics.csv has no rows")
            continue
        alpha = round(float(df["Alpha"].iloc[0]), 4)
        groups.setdefault(alpha, []).append(model_path)

    return dict(sorted(groups.items(), reverse=True))


def run_group(model_paths, device, trials, rng, args, tag):
    building_f1 = {name: [] for name in ALL_BUILDING_CLASSES}
    concept_designated_per_run = {name: [] for name in ALL_CONCEPTS}
    concept_designated_best_per_run = {name: [] for name in ALL_CONCEPTS}
    concept_polarity_per_run = {name: [] for name in ALL_CONCEPTS}
    concept_pooled_trials = {name: [] for name in ALL_CONCEPTS}

    concept_pool_size = num_concepts * 2

    for model_path in model_paths:
        print(f"[loading] {model_path}")
        building_pool_preds, concept_pool_preds, labels = get_predictions_and_labels(
            model_path, device, constants.BATCH_SIZE
        )

        building_labels = labels[:, :building_classes]
        concept_labels = labels[:, building_classes:building_classes + num_concepts]

        # Buildings are the final, directly-supervised output now -- neuron i is building i
        # by construction, so there is no meaningful random-neuron comparison here. Just
        # report plain classification F1 as a sanity check that training succeeded.
        for idx, name in enumerate(ALL_BUILDING_CLASSES):
            building_f1[name].append(f1_for_index(building_pool_preds, building_labels, idx, idx, invert=False))

        c_designated, c_best, c_polarity, c_trials = collect_group_results(
            concept_pool_preds, concept_labels, ALL_CONCEPTS, concept_pool_size,
            trials, rng, args.polarity_aware
        )
        for name in ALL_CONCEPTS:
            concept_designated_per_run[name].append(c_designated[name])
            concept_designated_best_per_run[name].append(c_best[name])
            concept_polarity_per_run[name].append(c_polarity[name])
            concept_pooled_trials[name].extend(c_trials[name])

    print(f"\n=== Building Label ({tag}), classification F1 (sanity check, no random baseline) ===")
    for name in ALL_BUILDING_CLASSES:
        print(f"{name:<20} {statistics.mean(building_f1[name])*100:>6.2f}%")

    print_summary_table(ALL_CONCEPTS, concept_designated_per_run, concept_designated_best_per_run,
                         concept_polarity_per_run, concept_pooled_trials, f"Concept ({tag})", args)



def main():
    parser = argparse.ArgumentParser(
        description="Compare each concept/building label's designated neuron F1 against F1 "
                    "under randomly-drawn neuron assignments. With --polarity-aware, both the "
                    "designated neuron and every random draw are scored at max(normal threshold "
                    "F1, inverted threshold F1), so the comparison stays fair when a label's "
                    "true polarity is not reliably anchored (common for equivalence-linked "
                    "concepts/buildings, since Equiv(a,b) = Equiv(1-a,1-b) is a tautology and "
                    "nothing in that axiom forces a specific polarity)."
    )
    parser.add_argument("model_paths", nargs="*", help="Explicit best_model.pth paths (single group mode).")
    parser.add_argument("--root-dir", type=Path, default=None,
                         help="Folder containing run*_outputs subfolders; grouped by alpha automatically.")
    parser.add_argument("--trials-per-run", type=int, default=40,
                         help="Number of random draws per model (default: 40).")
    parser.add_argument("--designated-only", action="store_true",
                         help="Skip random trials; just report the designated F1.")
    parser.add_argument("--polarity-aware", action="store_true",
                         help="Score both the designated neuron and every random draw at "
                              "max(F1 normal threshold, F1 inverted threshold), and report "
                              "which polarity won for the designated neuron.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--latex", action="store_true")
    args = parser.parse_args()

    if not args.root_dir and not args.model_paths:
        parser.error("Provide either --root-dir or explicit model_paths.")
    if args.root_dir and args.model_paths:
        parser.error("Use either --root-dir or explicit model_paths, not both.")

    rng = random.Random(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    trials = 0 if args.designated_only else args.trials_per_run

    if args.root_dir:
        groups = discover_runs_by_alpha(args.root_dir)
        if not groups:
            parser.error(f"No run folders with best_model.pth + metrics.csv found under {args.root_dir}")
        for alpha, model_paths in groups.items():
            print(f"\n########## alpha = {alpha} ({len(model_paths)} run(s)) ##########")
            run_group(model_paths, device, trials, rng, args, tag=f"alpha{alpha}")
    else:
        run_group([Path(p) for p in args.model_paths], device, trials, rng, args, tag="manual")


if __name__ == "__main__":
    main()