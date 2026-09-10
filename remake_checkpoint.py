import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# Self-contained copy of the CNN architecture -- does NOT import dissertation_workplace_script.py,
# since importing that file runs its training loop as a side effect. Keep this in sync manually
# if the architecture changes again.
class CNN(nn.Module):
    def __init__(self, nbr_of_neurons=17, num_classes=12, super_classes=3):
        super().__init__()
        self.conv1a = nn.Conv2d(3, 8, kernel_size=3)
        self.conv1b = nn.Conv2d(8, 16, kernel_size=3)
        self.conv2a = nn.Conv2d(16, 16, kernel_size=3)
        self.conv2b = nn.Conv2d(16, 32, kernel_size=3)
        self.conv3a = nn.Conv2d(32, 32, kernel_size=3)
        self.conv3b = nn.Conv2d(32, 64, kernel_size=3)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3)
        self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.globalAvgPooling = nn.AdaptiveAvgPool2d((1, 1))
        self.flatten = nn.Flatten()
        self.dropout = nn.Dropout(0.5)
        self.dense1 = nn.Linear(128, 64)
        self.concept_layer = nn.Linear(64, nbr_of_neurons)
        suport_layer1_nbr = math.ceil((nbr_of_neurons + num_classes) / 2)
        self.suport_layer1 = nn.Linear(nbr_of_neurons, suport_layer1_nbr)
        self.output_layer = nn.Linear(suport_layer1_nbr, num_classes)
        suport_layer2_nbr = math.ceil((num_classes + super_classes) / 2)
        self.suport_layer2 = nn.Linear(num_classes, suport_layer2_nbr)
        self.super_class_layer = nn.Linear(suport_layer2_nbr, super_classes)

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

        concepts = self.concept_layer(x)
        concepts_activation = F.leaky_relu(concepts)
        x = F.leaky_relu(self.suport_layer1(concepts_activation))
        buildings = self.output_layer(x)
        buildings_activation = F.leaky_relu(buildings)
        x2 = F.leaky_relu(self.suport_layer2(buildings_activation))
        super_classes_out = self.super_class_layer(x2)

        return torch.cat([buildings, concepts, super_classes_out], dim=1)


def make_checkpoint(run_dir, best_epoch, best_loss, learning_rate=0.0005, out_dir=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNN().to(device)
    model.load_state_dict(torch.load(f"{run_dir}/best_model.pth", map_location=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    checkpoint = {
        "epoch": best_epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_loss": best_loss,
        "best_epoch": best_epoch,
        "epochs_no_improve": 0,
        "torch_rng_state": torch.get_rng_state(),
        "numpy_rng_state": np.random.get_state(),
        "cuda_rng_state": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }
    dest = f"{out_dir or run_dir}/checkpoint.pth"
    torch.save(checkpoint, dest)
    print(f"Wrote {dest} from {run_dir}/best_model.pth (epoch {best_epoch}, loss {best_loss})")


if __name__ == "__main__":
    make_checkpoint(
        run_dir="outputs/testRun_NoPredicates_1LargeLayer_Sept_new/run0_outputs",
        best_epoch=39,
        best_loss=0.0350,
        learning_rate=0.0005,
    )