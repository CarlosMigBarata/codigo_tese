import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import torchvision.transforms as transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

import utils.rules_and_concepts as rules_and_concepts
import utils.constants as constants


# USAGE (Wide/1LargeLayer architecture)
# Buildings and concepts share a single 29-neuron layer here, unlike DSL's two
# separate pools. The designated-vs-random comparison for a building therefore
# draws its "random" alternatives from ALL 28 other neurons in that shared pool
# (including concept-slot neurons), not just the other 11 building-slot neurons.
# Saved CSVs reflect this: building/concept matrices both have 29 rows (the full
# shared pool), just a different subset of columns (labels).
# python3 neuron_concept_correlation_AUROC_wide.py --root-dir outputs/... --out-dir zzz_data_evaluation/...

DATA_ROOT = Path("/home/sofia/Desktop/datasets/datasetVCB")

ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
SUPER_CLASSES = rules_and_concepts.get_super_classes()
CLASSES = rules_and_concepts.get_all_classes()

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


# Same architecture as dissertation_workplace_script_1LargeLayer.py.
class CNN(nn.Module):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        super_classes = len(SUPER_CLASSES)
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

        all_concepts_nbr = nbr_of_neurons + num_classes
        self.all_concepts_layer = nn.Linear(64, all_concepts_nbr)

        suport_layer1_nbr = math.ceil((all_concepts_nbr + super_classes) / 2)
        self.suport_layer1 = nn.Linear(all_concepts_nbr, suport_layer1_nbr)

        self.super_class_layer = nn.Linear(suport_layer1_nbr, super_classes)

    def forward(self, inputs):
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

        concepts = self.all_concepts_layer(x)          # shared pool, width = 29
        concepts_activation = F.leaky_relu(concepts)

        x = F.leaky_relu(self.suport_layer1(concepts_activation))
        super_classes_activation = self.super_class_layer(x)

        result = torch.cat([concepts, super_classes_activation], dim=1)
        return result


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


@torch.no_grad()
def get_probabilities_and_labels(model_path, device, batch_size):
    model = CNN(in_channels=3, num_classes=building_classes).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    val_loader = load_val_loader(batch_size)

    all_pool_probs, all_labels = [], []
    for images, targets in val_loader:
        images = images.to(device)
        logits = model(images)
        pool_logits = logits[:, :concepts_pos]   # buildings+concepts share one layer, no separate slice

        all_pool_probs.append(torch.sigmoid(pool_logits).cpu())
        all_labels.append(targets)

    return torch.cat(all_pool_probs, dim=0), torch.cat(all_labels, dim=0)


def correlation_matrix(pool_probs, group_labels):
    x = pool_probs.numpy()
    y = group_labels.numpy()
    pool_size = x.shape[1]
    n_labels = y.shape[1]

    matrix = np.zeros((pool_size, n_labels))
    for i in range(pool_size):
        xi = x[:, i]
        xi_std = xi.std()
        for j in range(n_labels):
            yj = y[:, j]
            if xi_std == 0 or yj.std() == 0:
                matrix[i, j] = 0.0
            else:
                matrix[i, j] = np.corrcoef(xi, yj)[0, 1]
    return matrix


def auroc_matrix(pool_probs, group_labels):
    x = pool_probs.numpy()
    y = group_labels.numpy()
    pool_size = x.shape[1]
    n_labels = y.shape[1]

    matrix = np.full((pool_size, n_labels), 0.5)
    for i in range(pool_size):
        xi = x[:, i]
        for j in range(n_labels):
            yj = y[:, j]
            if len(np.unique(yj)) < 2:
                continue
            matrix[i, j] = roc_auc_score(yj, xi)
    return matrix


def plot_heatmap(matrix, names, title, out_path, vmin=-1, vmax=1, cbar_label="Pearson r"):
    fig, ax = plt.subplots(figsize=(max(6, len(names) * 0.5), max(6, matrix.shape[0] * 0.3)))
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=90)
    ax.set_yticks(range(matrix.shape[0]))
    ax.set_yticklabels([f"neuron {i}" for i in range(matrix.shape[0])])
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label=cbar_label)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def discover_runs_by_alpha(root_dir):
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


def run_group(model_paths, device, out_dir, tag):
    print(f"\n=== {tag} ({len(model_paths)} run(s)) ===")
    corr_matrices, auroc_matrices = [], []
    for model_path in model_paths:
        print(f"[loading] {model_path}")
        pool_probs, labels = get_probabilities_and_labels(model_path, device, constants.BATCH_SIZE)
        group_labels = labels[:, :concepts_pos]   # same order as ALL_BUILDING_CLASSES + ALL_CONCEPTS

        corr_matrices.append(correlation_matrix(pool_probs, group_labels))
        auroc_matrices.append(auroc_matrix(pool_probs, group_labels))

    avg_corr = np.mean(corr_matrices, axis=0)      # shape (29, 29): full shared pool x full label set
    avg_auroc = np.mean(auroc_matrices, axis=0)

    # Split columns (labels) into building/concept groups; keep all 29 rows (the
    # full shared pool) for both, since a building's random alternatives include
    # concept-slot neurons and vice versa.
    building_corr, concept_corr = avg_corr[:, :building_classes], avg_corr[:, building_classes:concepts_pos]
    building_auroc, concept_auroc = avg_auroc[:, :building_classes], avg_auroc[:, building_classes:concepts_pos]

    pd.DataFrame(building_corr, columns=ALL_BUILDING_CLASSES).to_csv(
        out_dir / f"building_neuron_correlation_{tag}.csv", index_label="neuron"
    )
    pd.DataFrame(concept_corr, columns=ALL_CONCEPTS).to_csv(
        out_dir / f"concept_neuron_correlation_{tag}.csv", index_label="neuron"
    )
    pd.DataFrame(building_auroc, columns=ALL_BUILDING_CLASSES).to_csv(
        out_dir / f"building_neuron_auroc_{tag}.csv", index_label="neuron"
    )
    pd.DataFrame(concept_auroc, columns=ALL_CONCEPTS).to_csv(
        out_dir / f"concept_neuron_auroc_{tag}.csv", index_label="neuron"
    )

    plot_heatmap(building_corr, ALL_BUILDING_CLASSES, f"Building-layer neuron correlation ({tag})",
                 out_dir / f"building_neuron_correlation_{tag}.png", vmin=-1, vmax=1, cbar_label="Pearson r")
    plot_heatmap(concept_corr, ALL_CONCEPTS, f"Concept-layer neuron correlation ({tag})",
                 out_dir / f"concept_neuron_correlation_{tag}.png", vmin=-1, vmax=1, cbar_label="Pearson r")
    plot_heatmap(building_auroc, ALL_BUILDING_CLASSES, f"Building-layer neuron AUROC ({tag})",
                 out_dir / f"building_neuron_auroc_{tag}.png", vmin=0, vmax=1, cbar_label="AUROC")
    plot_heatmap(concept_auroc, ALL_CONCEPTS, f"Concept-layer neuron AUROC ({tag})",
                 out_dir / f"concept_neuron_auroc_{tag}.png", vmin=0, vmax=1, cbar_label="AUROC")


def main():
    parser = argparse.ArgumentParser(
        description="Pearson correlation and AUROC between every neuron in the shared "
                    "Wide bottleneck layer and every concept/building label's ground truth."
    )
    parser.add_argument("model_paths", nargs="*", help="Explicit best_model.pth paths (single group mode).")
    parser.add_argument("--root-dir", type=Path, default=None,
                         help="Folder containing run*_outputs subfolders; grouped by alpha automatically.")
    parser.add_argument("--out-dir", type=Path, default=Path("."))
    args = parser.parse_args()

    if not args.root_dir and not args.model_paths:
        parser.error("Provide either --root-dir or explicit model_paths.")
    if args.root_dir and args.model_paths:
        parser.error("Use either --root-dir or explicit model_paths, not both.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.root_dir:
        groups = discover_runs_by_alpha(args.root_dir)
        if not groups:
            parser.error(f"No run folders with best_model.pth + metrics.csv found under {args.root_dir}")
        for alpha, model_paths in groups.items():
            tag = f"alpha{alpha}"
            run_group(model_paths, device, args.out_dir, tag)
    else:
        run_group([Path(p) for p in args.model_paths], device, args.out_dir, "manual")

    print(f"\nSaved matrices and heatmaps to {args.out_dir}")


if __name__ == "__main__":
    main()