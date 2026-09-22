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
# # Random-permutation comparison, 40 shuffles per run, pooled to 120 samples
# python3 random_neuron_baseline.py run0/best_model.pth run1/best_model.pth run2/best_model.pth --trials-per-run 40 --latex

# # Just the normal designated-neuron F1, averaged across the 3 runs, no permutation
# python3 random_neuron_baseline.py run0/best_model.pth run1/best_model.pth run2/best_model.pth --designated-only --latex

DATA_ROOT = Path("/home/sofia/Desktop/datasets/datasetVCB")

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
SUPER_CLASSES = rules_and_concepts.get_super_classes()
CLASSES = rules_and_concepts.get_all_classes()  # buildings + concepts + super_classes, in this order

building_classes = len(ALL_BUILDING_CLASSES)
num_concepts = len(ALL_CONCEPTS)
concepts_pos = building_classes + num_concepts

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
class CNN(nn.Module):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        nbr_of_neurons = min(len(ALL_CONCEPTS), 48)

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

        nbr_of_neurons = nbr_of_neurons * 2
        cnn_num_classes = num_classes * 2

        self.concept_layer = nn.Linear(64, nbr_of_neurons)

        suport_layer1_nbr = math.ceil((nbr_of_neurons + cnn_num_classes) / 2)
        self.suport_layer1 = nn.Linear(nbr_of_neurons, suport_layer1_nbr)

        self.output_layer = nn.Linear(suport_layer1_nbr, cnn_num_classes)

        suport_layer2_nbr = math.ceil((cnn_num_classes + len(SUPER_CLASSES)) / 2)
        self.suport_layer2 = nn.Linear(cnn_num_classes, suport_layer2_nbr)

        self.super_class_layer = nn.Linear(suport_layer2_nbr, len(SUPER_CLASSES))

    def forward(self, inputs):
        nbr_of_concepts = len(ALL_CONCEPTS)
        nbr_of_buildings = len(ALL_BUILDING_CLASSES)

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

        concepts_out = self.concept_layer(x)
        concepts_activation = F.leaky_relu(concepts_out)

        x = F.leaky_relu(self.suport_layer1(concepts_activation))
        buildings_out = self.output_layer(x)
        buildings_activation = F.leaky_relu(buildings_out)

        x2 = F.leaky_relu(self.suport_layer2(buildings_activation))
        super_classes_activation = self.super_class_layer(x2)

        out_buildings = buildings_out[:, :nbr_of_buildings]
        out_concepts = concepts_out[:, :nbr_of_concepts]

        result = torch.cat([out_buildings, out_concepts, super_classes_activation], dim=1)
        return result, buildings_out, concepts_out   # buildings: [batch,24], concepts: [batch,34]


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
    model = CNN(in_channels=3, num_classes=building_classes).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    val_loader = load_val_loader(batch_size)

    all_preds, all_labels = [], []
    for images, targets in val_loader:
        images = images.to(device)
        logits = model(images)
        probs = torch.sigmoid(logits)
        preds = (probs > 0.5).int().cpu()
        all_preds.append(preds)
        all_labels.append(targets.int())

    return torch.cat(all_preds, dim=0), torch.cat(all_labels, dim=0)


def f1_for_index(preds, labels, pred_idx, true_idx):
    y_pred = preds[:, pred_idx]
    y_true = labels[:, true_idx]
    tp = int(torch.sum((y_true == 1) & (y_pred == 1)))
    tn = int(torch.sum((y_true == 0) & (y_pred == 0)))
    fp = int(torch.sum((y_true == 0) & (y_pred == 1)))
    fn = int(torch.sum((y_true == 1) & (y_pred == 0)))
    return compute_f1(tp, tn, fp, fn)

def f1_for_index(preds, labels, pred_idx, true_idx):
    y_pred = preds[:, pred_idx]
    y_true = labels[:, true_idx]
    tp = int(torch.sum((y_true == 1) & (y_pred == 1)))
    tn = int(torch.sum((y_true == 0) & (y_pred == 0)))
    fp = int(torch.sum((y_true == 0) & (y_pred == 1)))
    fn = int(torch.sum((y_true == 1) & (y_pred == 0)))
    return compute_f1(tp, tn, fp, fn)

def collect_group_results(preds, labels, group_indices, names, trials, rng):
    """
    designated: {name: f1}       -- single deterministic pass, neuron i -> concept i
    trial_f1s:  {name: [f1,...]} -- one F1 per permutation trial (empty list if trials=0)
    """
    designated = {name: f1_for_index(preds, labels, idx, idx) for name, idx in zip(names, group_indices)}
    trial_f1s = {name: [] for name in names}

    for _ in range(trials):
        shuffled = group_indices.copy()
        rng.shuffle(shuffled)
        for name, true_idx, pred_idx in zip(names, group_indices, shuffled):
            trial_f1s[name].append(f1_for_index(preds, labels, pred_idx, true_idx))

    return designated, trial_f1s


def print_summary_table(names, designated_per_run, pooled_trials, group_label, args):
    print(f"\n=== {group_label} ===")
    header = f"{'Name':<20} {'Designated (avg)':>17}"
    if not args.designated_only:
        header += f" {'Random mean':>13} {'Random std':>12}"
    print(header)
    for name in names:
        avg_designated = statistics.mean(designated_per_run[name])
        line = f"{name:<20} {avg_designated*100:>16.2f}%"
        if not args.designated_only:
            pooled = pooled_trials[name]
            mean_f1 = statistics.mean(pooled)
            std_f1 = statistics.stdev(pooled) if len(pooled) > 1 else 0.0
            line += f" {mean_f1*100:>12.2f}% {std_f1*100:>11.2f}%"
        print(line)

    if args.latex:
        print(r"\begin{table}[htbp]")
        print(r"\centering")
        cols = "lc" if args.designated_only else "lccc"
        print(rf"\begin{{tabular}}{{{cols}}}")
        print(r"\hline")
        header_cells = rf"\textbf{{{group_label}}} & \textbf{{Designated (\%)}}"
        if not args.designated_only:
            header_cells += r" & \textbf{Random mean (\%)} & \textbf{Random std (\%)}"
        print(header_cells + r" \\")
        print(r"\hline")
        for name in names:
            avg_designated = statistics.mean(designated_per_run[name])
            row = f"{name} & {avg_designated*100:.2f}"
            if not args.designated_only:
                pooled = pooled_trials[name]
                mean_f1 = statistics.mean(pooled)
                std_f1 = statistics.stdev(pooled) if len(pooled) > 1 else 0.0
                row += f" & {mean_f1*100:.2f} & {std_f1*100:.2f}"
            print(row + r" \\")
        print(r"\hline")
        print(r"\end{tabular}")
        print(r"\caption{REPLACE ME}")
        print(rf"\label{{tab:REPLACE_ME_{group_label.lower().replace(' ', '_')}}}")
        print(r"\end{table}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare each concept/building label's designated neuron F1 (averaged "
                    "across the given runs) against F1 under randomly-permuted neuron "
                    "assignments, pooled across the same runs."
    )
    parser.add_argument("model_paths", nargs="+",
                         help="One or more best_model.pth checkpoints, e.g. the 3 seeds of one config.")
    parser.add_argument("--trials-per-run", type=int, default=40,
                         help="Number of random permutation shuffles per model (default: 40).")
    parser.add_argument("--designated-only", action="store_true",
                         help="Skip permutation trials; just report the normal (neuron i -> "
                              "concept i) F1, averaged across the given runs.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--latex", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    concept_indices = list(range(building_classes, concepts_pos))
    building_indices = list(range(0, building_classes))

    building_designated_per_run = {name: [] for name in ALL_BUILDING_CLASSES}
    concept_designated_per_run = {name: [] for name in ALL_CONCEPTS}
    building_pooled_trials = {name: [] for name in ALL_BUILDING_CLASSES}
    concept_pooled_trials = {name: [] for name in ALL_CONCEPTS}

    trials = 0 if args.designated_only else args.trials_per_run

    for model_path in args.model_paths:
        print(f"[loading] {model_path}")
        preds, labels = get_predictions_and_labels(Path(model_path), device, constants.BATCH_SIZE)

        b_designated, b_trials = collect_group_results(preds, labels, building_indices, ALL_BUILDING_CLASSES, trials, rng)
        c_designated, c_trials = collect_group_results(preds, labels, concept_indices, ALL_CONCEPTS, trials, rng)

        for name in ALL_BUILDING_CLASSES:
            building_designated_per_run[name].append(b_designated[name])
            building_pooled_trials[name].extend(b_trials[name])
        for name in ALL_CONCEPTS:
            concept_designated_per_run[name].append(c_designated[name])
            concept_pooled_trials[name].extend(c_trials[name])

    print_summary_table(ALL_BUILDING_CLASSES, building_designated_per_run, building_pooled_trials, "Building Label", args)
    print_summary_table(ALL_CONCEPTS, concept_designated_per_run, concept_pooled_trials, "Concept", args)


if __name__ == "__main__":
    main()