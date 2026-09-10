import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

import utils.rules_and_concepts as rules_and_concepts

ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()

building_classes = len(ALL_BUILDING_CLASSES)


# Self-contained copy of the CNN architecture -- does NOT import dissertation_workplace_script.py,
# since importing that file runs its training loop as a side effect. Keep this in sync manually
# if the architecture changes again.
class CNN(nn.Module):
    def __init__(self, num_classes=12, super_classes=3, name="cnn_model"):

        """
        Building blocks of convolutional neural network.

        Parameters:
            * in_channels: Number of channels in the input image (for grayscale images, 1)
            * num_classes: Number of classes to predict. In our problem, 10 (i.e digits from  0 to 9).
        """
        super(CNN, self).__init__()

        #nbr_of_concepts = len(CLASSES) - final_classes

        nbr_of_neurons = min(len(ALL_CONCEPTS), 48)

        #layers #era 16,32,64
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
        self.dropout = nn.Dropout(0.5)

        self.dense1 = nn.Linear(128, 64)
        #self.dense2 = nn.Linear(128, 64)




        '''
        
        self.concept_layer = nn.Linear(64, nbr_of_neurons)

        self.output_layer = nn.Linear(nbr_of_neurons, num_classes) #nbr_of_neurons

        self.super_class_layer = nn.Linear(num_classes, super_classes)#num_classes
        '''

        all_concepts_nbr = nbr_of_neurons + num_classes
        self.all_concepts_layer = nn.Linear(64, all_concepts_nbr)

        suport_layer1_nbr = math.ceil((all_concepts_nbr + super_classes) / 2) 
        self.suport_layer1 = nn.Linear(all_concepts_nbr, suport_layer1_nbr)

        self.super_class_layer = nn.Linear(suport_layer1_nbr, super_classes)#num_classes



    def forward(self, inputs):
        """
        Define the forward pass of the neural network.

        Parameters:        
            x: Input tensor.

        Returns:
            torch.Tensor
                The output tensor after passing through the network.
        """
        if isinstance(inputs, (list, tuple)):
            inputs = inputs[0]


        x = F.leaky_relu(self.conv1a(inputs))
        x = F.leaky_relu(self.conv1b(x))
        x = self.maxpool(x)

        x = F.leaky_relu(self.conv2a(x))
        x = self.maxpool(x) #new
        x = F.leaky_relu(self.conv2b(x))
        x = self.maxpool(x)
        
        x = F.leaky_relu(self.conv3a(x))
        #x = self.maxpool(x) #new
        x = F.leaky_relu(self.conv3b(x))
        x = self.maxpool(x)

        x = F.leaky_relu(self.conv4(x))

        x = self.globalAvgPooling(x)
        x = self.flatten(x)
        #x = self.dropout(x)

        
        x = F.leaky_relu(self.dense1(x))
        #x = self.dropout(x)
        #x = F.leaky_relu(self.dense2(x))

        concepts = self.all_concepts_layer(x)

        concepts_activation = F.leaky_relu(concepts)

        x = F.leaky_relu(self.suport_layer1(concepts_activation))


        super_classes_activation = self.super_class_layer(x)

        result = torch.cat([concepts, super_classes_activation], dim=1)
        return result


def make_checkpoint(run_dir, best_epoch, best_loss, learning_rate=0.0005, out_dir=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNN(num_classes=building_classes).to(device)
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
        run_dir="outputs/testRun_NoPredicates_1LargeLayer_Sept_new/run2_outputs",
        best_epoch=30,
        best_loss=0.1320,
        learning_rate=0.0005,
    )