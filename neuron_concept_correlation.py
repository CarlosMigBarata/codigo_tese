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

import utils.rules_and_concepts as rules_and_concepts
import utils.constants as constants


# USAGE
# Point at a folder containing run*_outputs subfolders; each run's alpha is read
# from its metrics.csv, runs are grouped by alpha, and one set of results is
# produced per alpha group.
# python3 neuron_concept_correlation.py --root-dir outputs/to_send/to_send_to_GPU_onlyEquiv --out-dir zzz_data_evaluation
#
# Old explicit-paths mode still works if you want a single combined group:
# python3 neuron_concept_correlation.py run0/best_model.pth run1/best_model.pth run2/best_model.pth --out-dir zzz_data_evaluation

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


# Same architecture as dissertation_workplace_script_double_sized_layers.py.
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
        return result, buildings_out, concepts_out


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

    all_building_probs, all_concept_probs, all_labels = [], [], []
    for images, targets in val_loader:
        images = images.to(device)
        _, buildings_out, concepts_out = model(images)

        all_building_probs.append(torch.sigmoid(buildings_out).cpu())
        all_concept_probs.append(torch.sigmoid(concepts_out).cpu())
        all_labels.append(targets)

    return (torch.cat(all_building_probs, dim=0),
            torch.cat(all_concept_probs, dim=0),
            torch.cat(all_labels, dim=0))


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


def plot_heatmap(matrix, names, title, out_path):
    fig, ax = plt.subplots(figsize=(max(6, len(names) * 0.5), max(6, matrix.shape[0] * 0.3)))
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=90)
    ax.set_yticks(range(matrix.shape[0]))
    ax.set_yticklabels([f"neuron {i}" for i in range(matrix.shape[0])])
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label="Pearson r")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


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


def run_group(model_paths, device, out_dir, tag):
    print(f"\n=== {tag} ({len(model_paths)} run(s)) ===")
    building_matrices, concept_matrices = [], []
    for model_path in model_paths:
        print(f"[loading] {model_path}")
        building_probs, concept_probs, labels = get_probabilities_and_labels(
            model_path, device, constants.BATCH_SIZE
        )
        building_labels = labels[:, :building_classes]
        concept_labels = labels[:, building_classes:concepts_pos]

        building_matrices.append(correlation_matrix(building_probs, building_labels))
        concept_matrices.append(correlation_matrix(concept_probs, concept_labels))

    avg_building_matrix = np.mean(building_matrices, axis=0)
    avg_concept_matrix = np.mean(concept_matrices, axis=0)

    pd.DataFrame(avg_building_matrix, columns=ALL_BUILDING_CLASSES).to_csv(
        out_dir / f"building_neuron_correlation_{tag}.csv", index_label="neuron"
    )
    pd.DataFrame(avg_concept_matrix, columns=ALL_CONCEPTS).to_csv(
        out_dir / f"concept_neuron_correlation_{tag}.csv", index_label="neuron"
    )

    plot_heatmap(avg_building_matrix, ALL_BUILDING_CLASSES, f"Building-layer neuron correlation ({tag})",
                 out_dir / f"building_neuron_correlation_{tag}.png")
    plot_heatmap(avg_concept_matrix, ALL_CONCEPTS, f"Concept-layer neuron correlation ({tag})",
                 out_dir / f"concept_neuron_correlation_{tag}.png")


def main():
    parser = argparse.ArgumentParser(
        description="Pearson correlation between every neuron in the concept/building "
                    "layer (full unsliced pool) and every concept/building label's "
                    "ground truth. Either point at a folder of run*_outputs subfolders "
                    "(--root-dir), grouped automatically by the alpha recorded in each "
                    "run's metrics.csv, or pass explicit checkpoint paths for a single "
                    "combined group."
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