
import math
import time
import ltn
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
import sys

from PIL import Image
import os

import torch
from torch import optim
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torch.utils.data import Subset
#from tqdm import tqdm

# !pip install torchvision
import torchvision

import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torchvision.models as models
from datetime import datetime
import importlib
import subprocess
import json
import utils.constants as constants
#from utils.axioms import compute_axioms, get_number_of_final_classes, get_CLASSES
#from utils.occlusion import occlusion_map, show_occlusion


# !pip install torchmetrics
import torchmetrics

if len(sys.argv) < 2:
    print("Usage: python3 dissertation_workplace_script.py <runName>")
    sys.exit(1)

RUN_NAME = sys.argv[1]


""" HYPERPARAMETERS """


DATA_ROOT = Path("/home/sofia/Desktop/datasets/datasetVCB")
#DATA_ROOT = Path("/home/sofia/Desktop/datasets/newDataset1/full_run/")
BATCH_SIZE = constants.BATCH_SIZE
COMPLEXITY_DATASET = constants.COMPLEXITY_DATASET
TOTAL_EXAMPLES = constants.TOTAL_EXAMPLES
LEARNING_RATE = constants.LEARNING_RATE
csv_path = "results.csv"
txt_path = "stats.txt"
confusion_matrix_path = "conf_matrix.txt"

EPOCHS = constants.EPOCHS
EARLY_STOPPING_DELTA = constants.EARLY_STOPPING_DELTA
PATIENCE = constants.PATIENCE
MODEL_SAVING_INTERVAL = constants.MODEL_SAVING_INTERVAL
DEBUG_MODE = constants.DEBUG_MODE

TRAIN_WITH_A_SUBSET = constants.TRAIN_WITH_A_SUBSET
SUBSET_SIZE = constants.SUBSET_SIZE
STRATIFY = constants.STRATIFY
SUBSET_SEED = constants.SUBSET_SEED
VALIDATION_INTERVAL = constants.VALIDATION_INTERVAL
#default 42



print(f"Starting execution using DEBUG_MODE: {DEBUG_MODE}")
print(f"Starting execution using TRAIN_WITH_A_SUBSET: {TRAIN_WITH_A_SUBSET}")

if TRAIN_WITH_A_SUBSET: print(f"SUBSET SIZE: {SUBSET_SIZE}, SUBSET_SEED: {SUBSET_SEED}, STRATIFY:{STRATIFY} ")

#print("pode ser necessario de reiniciar duas vezes apos mudar o conhecimento no dicionario das regras\n")

#from utils.axioms import compute_axioms, get_number_of_final_classes, get_CLASSES
import utils.axioms as axioms
import utils.occlusion as occlusion
import utils.rules_and_concepts as rules_and_concepts
import utils.test_new_rules as test_new_rules
import utils.constants as constants
import utils.outputs_and_prints as outputs_and_prints
#import charter
importlib.reload(rules_and_concepts)
importlib.reload(axioms)
importlib.reload(occlusion)
importlib.reload(test_new_rules)
importlib.reload(constants)
importlib.reload(outputs_and_prints)
#importlib.reload(charter)



data_path = Path(DATA_ROOT, "C" + str(COMPLEXITY_DATASET))
labels = Path(DATA_ROOT, "all.csv")
images = Path(DATA_ROOT, "c1")

df = pd.read_csv(labels, index_col=0)
df["id"] = df["id"].apply(lambda x: f"{x}.jpg")
# CLASSES = df.columns.tolist()[1:]

CLASSES = rules_and_concepts.get_all_classes() #era get_classes

ALL_EXISTING_CLASSES = rules_and_concepts.get_all_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
SUPER_CLASSES = rules_and_concepts.get_super_classes()



building_classes = len(ALL_BUILDING_CLASSES)
super_classes = len(rules_and_concepts.get_super_classes())
concepts = len(ALL_CONCEPTS)


concepts_pos = building_classes + concepts
super_classes_pos = concepts_pos + super_classes


assert CLASSES[:building_classes] == rules_and_concepts.get_all_building_classes(), \
    f"Building classes mismatch: {CLASSES[:building_classes]}"
assert len(CLASSES) <= building_classes + len(ALL_CONCEPTS) + 5, \
    f"CLASSES too long for model output: {len(CLASSES)} vs {building_classes + len(ALL_CONCEPTS) + 5}"
print(f"[DEBUG] CLASSES order: {CLASSES}")
print(f"[DEBUG] Building classes (first {building_classes}): {CLASSES[:building_classes]}")
print(f"[DEBUG] Concepts (from {building_classes} to {concepts_pos}): {CLASSES[building_classes:concepts_pos]}")
print(f"[DEBUG] Super classes (after): {CLASSES[concepts_pos:]}")

#print(f"final classes: {final_classes}, number of classes {len(CLASSES)}, CLASSES in main file: {CLASSES}")

class BuildingsDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None):
        self.df = dataframe.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        img_path = self.img_dir / row["id"]
        image = Image.open(img_path).convert("RGB")



        #target = torch.tensor(row[CLASSES].values, dtype=torch.float32)
        target = torch.tensor(row[CLASSES].to_numpy(dtype=float), dtype=torch.float32)


        if self.transform:
            image = self.transform(image)

        return image, target, row["id"]


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def random_subset(dataset, n, seed=42):
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(dataset), size=n, replace=False)
    return Subset(dataset, indices.tolist())


def stratified_subset(dataset, df, n, stratify_class, seed=42):
    """Stratify on a single (usually rare) class to preserve its positive rate."""
    rng = np.random.default_rng(seed)
    labels = df[stratify_class].to_numpy()  # fast: no image loading
    pos = np.where(labels == 1)[0]
    neg = np.where(labels == 0)[0]

    pos_ratio = len(pos) / len(labels)
    n_pos = int(round(n * pos_ratio))
    n_neg = n - n_pos

    # Guard against asking for more than exists
    n_pos = min(n_pos, len(pos))
    n_neg = min(n_neg, len(neg))

    chosen = np.concatenate([
        rng.choice(pos, size=n_pos, replace=False),
        rng.choice(neg, size=n_neg, replace=False),
    ])
    rng.shuffle(chosen)  # mix pos/neg so batches aren't blocky
    return Subset(dataset, chosen.tolist())


TRAIN_TEST_LIMIT = int(0.8 * len(df))

train_df = df[:TRAIN_TEST_LIMIT]
test_df = df[TRAIN_TEST_LIMIT:]

df[CLASSES] = df[CLASSES].apply(pd.to_numeric)


train_dataset = BuildingsDataset(train_df, images, transform=transform)
LEN_TRAIN_DATASET= len(train_dataset)
test_dataset = BuildingsDataset(test_df, images, transform=transform)

subset_class_pos_rates = ""
info_about_dataset = ""
train_set_df =train_df

if TRAIN_WITH_A_SUBSET:
    stratified_class = "Machine"

    if STRATIFY:

        train_subset = stratified_subset(
            train_dataset, train_df,
            n=SUBSET_SIZE,
            stratify_class=stratified_class,   # or your rarest class
            seed=SUBSET_SEED,
        )
        #train_set = train_subset
    else:
        train_subset = random_subset(train_dataset, n=SUBSET_SIZE, seed=SUBSET_SEED)
    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True)

    print(f"[subset] using {len(train_subset)}/{len(train_dataset)} train samples (stratified={STRATIFY}, stratified_class={stratified_class}, seed={SUBSET_SEED})")
    info_about_dataset = f"[subset] using {len(train_subset)}/{len(train_dataset)} train samples (stratified={STRATIFY}, seed={SUBSET_SEED})"
    
    subset_df = train_df.iloc[train_subset.indices]
    train_set_df = subset_df
    print("[subset] class positive rates:")
    print(subset_df[CLASSES].mean().to_string())
    subset_class_pos_rates = subset_df[CLASSES].mean().to_string()
else:
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)





#print(train_df["Cafe"])

"""CNN MODEL"""

class CNN(nn.Module):
    def __init__(self, in_channels, num_classes, name="cnn_model"):

        """
        Building blocks of convolutional neural network.

        Parameters:
            * in_channels: Number of channels in the input image (for grayscale images, 1)
            * num_classes: Number of classes to predict. In our problem, 10 (i.e digits from  0 to 9).
        """
        super(CNN, self).__init__()

        #nbr_of_concepts = len(CLASSES) - final_classes

        nbr_of_neurons = min(len(ALL_CONCEPTS) + 5, 48)

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


        '''
        
        
        '''
        #3 conv 43624, 4 conv 18432 com 6 é 13824

        '''
        
        size = self._get_flattened_size() 
        print(f"size of CNN {size}, concept layer: {nbr_of_neurons}")
        '''


        ''' 


        '''




    def _get_flattened_size(self):
        with torch.no_grad():
            x = torch.zeros(1, 3, 224, 224)
            x = F.relu(self.conv1a(x))
            x = F.relu(self.conv1b(x))
            x = self.maxpool(x)

            x = F.relu(self.conv2a(x))
            x = F.relu(self.conv2b(x))
            x = self.maxpool(x)

            x = F.relu(self.conv3a(x))
            #x = F.relu(self.conv3b(x))
            x = self.maxpool(x)

            return x.view(1, -1).shape[1]


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

        y = F.leaky_relu(self.all_concepts_layer(x))  

        x = F.leaky_relu(self.suport_layer1(y))

        x = self.super_class_layer(x)

        result = torch.cat([y, x], dim=1)
        return result

      
'''
class CNN(nn.Module):
    def __init__(self, in_channels, num_classes, name="cnn_model"):
        super().__init__()

        self.conv1 = nn.Conv2d(3, 16, 3)
        self.conv2 = nn.Conv2d(16, 32, 3)
        self.conv3 = nn.Conv2d(32, 64, 3)

        self.pool = nn.MaxPool2d(2)

        self.gap = nn.AdaptiveAvgPool2d((1,1))

        self.fc1 = nn.Linear(64, 128)
        self.fc2 = nn.Linear(128, 64)

        self.concept_layer = nn.Linear(64, 32)
        self.output_layer = nn.Linear(32, num_classes)

    def forward(self, x):

        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))

        x = self.gap(x)
        x = torch.flatten(x, 1)

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        y = F.relu(self.concept_layer(x))
        x = self.output_layer(y)

        return torch.cat([x, y], dim=1)

'''
class PredicateModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.activation = nn.Sigmoid()

    def forward(self, logits, class_idx):
        probs = self.activation(logits)  # [batch, num_classes]

        # Make sure class_idx is the same shape as batch
        if class_idx.dim() == 0:
            class_idx = class_idx.repeat(logits.shape[0])

        # Use torch.arange to select batch elements along dim 0
        selected = probs[torch.arange(probs.size(0)), class_idx.long()]

        return selected  # [batch]



# Predicates
#final classes = 4
def reset_model(in_channels, num_classes, seed=None):
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    #print("\n\n\n\n problem in reset model??? \n\n\n\n")

    logits_model = CNN(in_channels=in_channels, num_classes=num_classes)#3, final classes
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logits_model = logits_model.to(device)

    # compute pos_weight from training data
    class_cols = CLASSES[:building_classes]
    print(f"class_cols: {class_cols}")
    pos_counts = train_set_df[class_cols].sum()
    neg_counts = len(train_set_df) - pos_counts
    weights = (neg_counts / pos_counts.clip(lower=1)).values
    pos_weight = torch.tensor(weights, dtype=torch.float32).to(device)


    #missCounter = 0
    #pos_weight é basicamente a razão entre o numero de casos positvos e os negativos. a ideia é que o modelo deve penalizar um falso errado proporicionalmente mais,
    #porque existe mais errados do que falsos
    #So for Restaurant (12% positive, 88% negative), the weight would be ~7.2. Missing a "this is a Restaurant" prediction now costs 7.2x more than incorrectly predicting "this is a Restaurant" when it isn't.
    classification_loss_fn = nn.BCEWithLogitsLoss() #pos_weight=pos_weight


    super_cols = CLASSES[concepts_pos:super_classes_pos]
    super_pos_counts = train_set_df[super_cols].sum()
    super_neg_counts = len(train_set_df) - super_pos_counts
    super_weights = (super_neg_counts / super_pos_counts.clip(lower=1)).values
    super_pos_weight = torch.tensor(super_weights, dtype=torch.float32).to(device)
    super_loss_fn = nn.BCEWithLogitsLoss() #pos_weight=super_pos_weight

    p = ltn.Predicate(PredicateModel())

    return logits_model, device,classification_loss_fn, super_loss_fn, p


def __get_elements_from_batch(batch_elements):
    #print("\n\n\n problems in get_elems? \n\n\n")
    features_calculated = batch_elements[0]
    inverted_labels_list = batch_elements[1]
    #labels_list = np.transpose(inverted_labels_list)
    labels_list = inverted_labels_list.T
    return features_calculated, labels_list



""" TRAINING FUNCTIONS """

class Counter:
    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.value = 0.0

    def update(self, value):
        self.value = value

    def result(self):
        return self.value

class MeanMetric:
    def __init__(self):
        self.reset_state()

    def update(self, value, n=1):
        self.total += value * n
        self.count += n

    def compute(self):
        return self.total / self.count if self.count != 0 else 0.0


    def reset_state(self):
        self.total = 0.0
        self.count = 0

    def result(self):
        return self.compute()
    

class RunningAverage:
    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.total = 0
        self.count = 0

    def update(self, value):
        self.total += value
        self.count += 1

    
    def result(self):
        if self.count == 0:
            return 0
        return self.total / self.count


metrics_dict = {
    "train_sat_kb": MeanMetric(),
    "val_sat_kb": MeanMetric(),
    "train_loss": RunningAverage(),
    "val_loss": RunningAverage(),
    "combined_val_loss": RunningAverage(),
    "combined_train_loss": RunningAverage(),
    "alpha": Counter()
}

class_train_accuracy_metric = {
    f"{class_name.lower()}_train_accuracy": MeanMetric()
    for class_name in CLASSES
}

metrics_dict.update(class_train_accuracy_metric)

class_val_accuracy_metric = {
    f"{class_name.lower()}_val_accuracy": MeanMetric()
    for class_name in CLASSES
}
metrics_dict.update(class_val_accuracy_metric)


classes_for_confusion_matrix = rules_and_concepts.get_classes()


conf_matrices = {
    f"{cls}_train": torch.zeros(2, 2, dtype=torch.int32)
    for cls in classes_for_confusion_matrix
}

conf_matrices.update({
    f"{cls}_val": torch.zeros(2, 2, dtype=torch.int32)
    for cls in classes_for_confusion_matrix
})

'''
model steps

'''


def train_step(features_param, *labels_list, optimizer, logits_model, classification_loss_fn, super_loss_fn, p, alpha=0.5):

    if not hasattr(train_step, "_verified"):
        train_step._verified = True
        print(f"[DEBUG] labels_list length: {len(labels_list)}, final_classes: {building_classes}")
        print(f"[DEBUG] class labels map to: {CLASSES[:building_classes]}")
        print(f"[DEBUG] concepts labels map to: {CLASSES[building_classes:concepts_pos]}")
        print(f"[DEBUG] Super classes labels map to: {CLASSES[concepts_pos:]}")
        logits = logits_model(features_param)
        print(f"[DEBUG] logits shape: {logits.shape}, expected: [batch, {building_classes + min(len(ALL_CONCEPTS)+5, 48)}]")


    logits_model.train()
    optimizer.zero_grad()

    start = time.time()
    logits = logits_model(features_param)
    end = time.time()

    timeDifLogits = end-start

    # first 4 logits correspond to classes

    #class_logits = logits[:, :building_classes]
    #class_labels = torch.stack(labels_list[:building_classes], dim=1).float()
    #building_loss = classification_loss_fn(class_logits, class_labels)

    startLTN = time.time()

    super_class_logits = logits[:, concepts_pos:super_classes_pos]
    super_class_labels = torch.stack(list(labels_list[concepts_pos:super_classes_pos]), dim=1).float()

    super_loss = super_loss_fn(super_class_logits, super_class_labels)

    classification_loss = super_loss    
    
    
    complete_lables_tensor = torch.stack(labels_list, dim=1).float()

    sat = axioms.compute_axioms(logits, *labels_list, p=p, debug_mode=DEBUG_MODE, validation_mode=False)

    ltn_loss = 1.0 - sat

    # ----- Combined loss -----



    loss = alpha * classification_loss + (1 - alpha) * ltn_loss

    loss.backward()
    optimizer.step()

    print(f"Sat Function Result: {sat.item()}, Class_loss: {classification_loss}, ltn-loss: {ltn_loss}, Combined_loss:{loss} ")

    # Update metric
    metrics_dict["train_sat_kb"].update(sat.item())
    metrics_dict["train_loss"].update(classification_loss.item())
    metrics_dict["combined_train_loss"].update(loss.item())

    #predictions = logits

    calculate_accuracy_for_each_class("train", logits, labels_list)
    update_confusion_matrix("train", logits.detach(), complete_lables_tensor, CLASSES, conf_matrices)

    endLTN = time.time()

    timeDifLTN = endLTN - startLTN

    #print(f"logits time: {timeDifLogits}, timeLTN: {timeDifLTN}")

    return timeDifLogits, timeDifLTN

@torch.no_grad()
def test_step(features_param, *labels_list, logits_model, classification_loss_fn, super_loss_fn, p, alpha=0.5):
    logits_model.eval()

    logits = logits_model(features_param)
        
    class_logits = logits[:, :building_classes]
    class_labels = torch.stack(labels_list[:building_classes], dim=1).float()
    building_loss = classification_loss_fn(class_logits, class_labels)

    super_class_logits = logits[:, concepts_pos:super_classes_pos]
    super_class_labels = torch.stack(list(labels_list[concepts_pos:super_classes_pos]), dim=1).float()
    super_loss = super_loss_fn(super_class_logits, super_class_labels)

    classification_loss = super_loss
    
    
    complete_lables_tensor = torch.stack(labels_list, dim=1).float()

    sat_kb = axioms.compute_axioms(logits, *labels_list, p=p, debug_mode=DEBUG_MODE, validation_mode=True)

    ltn_loss = 1.0 - sat_kb

    # ----- Combined loss -----
    loss = alpha * classification_loss + (1 - alpha) * ltn_loss


    metrics_dict["val_sat_kb"].update(sat_kb.item())
    metrics_dict["val_loss"].update(classification_loss.item())
    metrics_dict["combined_val_loss"].update(loss.item())

    calculate_accuracy_for_each_class("val", logits, labels_list)
    update_confusion_matrix("val", logits.detach(), complete_lables_tensor, CLASSES, conf_matrices)


""" AUXILIARY FUNCTIONS """


'''conf matrix '''

def update_confusion_matrix(phase, logits, labels, class_names, conf_matrices):
    """
    predictions: tensor (batch_size, num_classes) -> logits
    labels: tensor (batch_size, num_classes)
    """
    probs = torch.sigmoid(logits[:, :len(class_names)])
    preds = (probs > 0.5).int()

    for i, class_name in enumerate(class_names):
        if class_name not in classes_for_confusion_matrix:
            continue

        y_true = labels[:, i].int()
        y_pred = preds[:, i]

        # Compute confusion matrix manually
        tn = torch.sum((y_true == 0) & (y_pred == 0)) #TN
        fp = torch.sum((y_true == 0) & (y_pred == 1)) #FP
        fn = torch.sum((y_true == 1) & (y_pred == 0)) #FN
        tp = torch.sum((y_true == 1) & (y_pred == 1)) 

        cm = torch.tensor([[tn, fp],
                           [fn, tp]], dtype=torch.int32)

        conf_matrices[f"{class_name}_{phase}"] += cm


def reset_conf_matrices(conf_matrices):
    for key in conf_matrices:
        conf_matrices[key].zero_()


def calculate_accuracy_for_each_class(phase, logits, labels_param):
    probs = torch.sigmoid(logits)

    for i, class_name in enumerate(CLASSES):
        class_labels = labels_param[i].float()

        y_pred = probs[:, i]
        y_pred = (y_pred > 0.5).float()

        accuracy = (y_pred == class_labels).float().mean()

        metrics_dict[f"{class_name.lower()}_{phase}_accuracy"].update(
            accuracy.item()
        )




'''CLINGO'''

def export_predictions_to_csv_and_lp(model_path, output_csv_path, raw_output_csv_path, output_lp_path, sample_loader=test_loader):

    logits_model, device, _, _, p = reset_model(in_channels=3, num_classes=building_classes)

    logits_model.load_state_dict(torch.load(model_path))
    logits_model.to(device)
    logits_model.eval() #CNN model in eval mode. if its in train mode, the dropout layers mess up the results bc they have different values

    rows = []
    raw_rows = []

    with torch.no_grad():
        for batch_elements in sample_loader:
            features_param, _ = __get_elements_from_batch(batch_elements)
            ids = batch_elements[2]

            features_param = features_param.to(device)

            logits = logits_model(features_param)
            probs = torch.sigmoid(logits)

            # move to cpu
            #probs = probs.cpu().numpy()

            for j, sample in enumerate(probs):
                sid = axioms.make_sid(ids[j])
                row = {"sample_id": sid}
                r_row = {"sample_id": sid}
                for i, class_name in enumerate(CLASSES):
                    row[class_name] = int(sample[i] > 0.5)
                    r_row[class_name] = sample[i]
                rows.append(row)
                raw_rows.append(r_row)

    df_out = pd.DataFrame(rows)
    df_out.to_csv(output_csv_path, index=False)

    raw_df_out = pd.DataFrame(raw_rows)
    raw_df_out.to_csv(raw_output_csv_path, index=False)

    #df_out = pd.read_csv(csv_path)

    with open(output_lp_path, "w") as f:
        for _, row in df_out.iterrows():
            sid = row["sample_id"]
            f.write(f"sample({sid}).\n")
            f.write(f"holds({sid}, building).\n")
            f.write(f"holds({sid}, feature).\n")

            for col in df_out.columns:
                if col == "sample_id":
                    continue
                if row[col] == 1:
                    atom = col.lower()
                    f.write(f"holds({sid}, {atom}).\n")

            f.write("\n")


    print(f"Saved predictions to {output_csv_path}, {raw_output_csv_path} and {output_lp_path}")

    return logits_model, device, p



def run_clingo(lp_output, lp_to_run="utils/rules.lp"):
    #cmd = f"clingo utils/rules.lp {lp_output} --outf=2"
    result = subprocess.run(
    ["clingo", lp_to_run, lp_output, "--outf=2"],
    capture_output=True,
    text=True
)
    return result.stdout, result.stderr


def extract_rule_counts(clingo_output):
    #print(f"clingo out {clingo_output}")
    
    data = json.loads(clingo_output)

    #print(f"data {data}")

    rule_holds_counts = {}
    rule_vacuously_holds_count = {}
    violation_type_counts = defaultdict(dict)
    clingo_out_per_sample = defaultdict(dict)

    #print(f"data: {data}")

    for call in data["Call"]:
        for witness in call["Witnesses"]:
            for atom in witness["Value"]:

                if atom.startswith("rule_holds_count"):
                    # violation_count(rule, N)
                    inside = atom[len("rule_holds_count("):-1]
                    rule, n = inside.split(",")
                    rule_holds_counts[rule.strip()] = int(n.strip())

                elif atom.startswith("rule_vacuously_holds_count"):
                    # violation_count(rule, N)
                    inside = atom[len("rule_vacuously_holds_count("):-1]
                    rule, n = inside.split(",")
                    rule_vacuously_holds_count[rule.strip()] = int(n.strip())


                elif atom.startswith("violation_type_count"):
                    # violation_type_count(rule, type, N)
                    inside = atom[len("violation_type_count("):-1]
                    rule, vtype, n = inside.split(",")

                    rule = rule.strip()
                    vtype = vtype.strip()
                    n = int(n.strip())

                    violation_type_counts[rule][vtype] = n
                
                elif atom.startswith("rule_holds"):
                    inside = atom[len("rule_holds("):-1]
                    sample, rule_name = inside.split(",")
                    clingo_out_per_sample[sample.strip()][rule_name.strip()] = 1

                elif atom.startswith("rule_not_holds"):
                    inside = atom[len("rule_not_holds("):-1]
                    sample, rule_name, vtype = inside.split(",")
                    clingo_out_per_sample[sample.strip()][rule_name.strip()] = 0

                elif atom.startswith("rule_vacuously_holds"):
                    inside = atom[len("rule_vacuously_holds("):-1]
                    sample, rule_name = inside.split(",")
                    clingo_out_per_sample[sample.strip()][rule_name.strip()] = 1

    return rule_holds_counts, rule_vacuously_holds_count, violation_type_counts, clingo_out_per_sample


def compute_consistency_per_rule(clingo_output, txt_file):
    rule_holds_counts, rule_vacuously_holds_count, violation_type_counts, clingo_out_per_sample = extract_rule_counts(clingo_output)

    consistency = {}
    all_rules = set(rule_holds_counts.keys()) | set(violation_type_counts.keys()) | set(rule_vacuously_holds_count.keys())

    for rule in all_rules:
        holds = rule_holds_counts.get(rule, 0)
        violations = sum(violation_type_counts.get(rule, {}).values())
        #vac_holds = rule_vacuously_holds_count.get(rule, 0)
        total = holds + violations

        if total == 0:
            consistency[rule] = -2.0  # no samples → undefined
        else:
            consistency[rule] = holds / total  # fraction of times the rule is satisfied

    rules_and_concepts.print_only_active_rules(
        consistency, rule_holds_counts, rule_vacuously_holds_count, violation_type_counts, txt_file
    )

    return consistency, clingo_out_per_sample


def debug_batch_alignment(loader, logits_model, device):
    batch = next(iter(loader))
    features, labels, ids = batch
    features = features.to(device)
    with torch.no_grad():
        logits = logits_model(features)
    probs = torch.sigmoid(logits)
    print(f"\n[DEBUG] Sample: {ids[0]}")
    for i, cls in enumerate(CLASSES):
        label = labels[0, i].item()
        pred = probs[0, i].item()
        print(f"  {cls:20s}  label={int(label)}  pred={pred:.3f}")
    



#final_epochs: epochs with final alpha
def new_calculate_alpha(epoch= 0, warmup_epochs = 10, final_alpha = 0.25, final_epochs=30, starting_alpha=1.0):
    alpha = starting_alpha


    if epoch < warmup_epochs:
        alpha = starting_alpha
    elif epoch < EPOCHS - final_epochs:
        progress = (epoch - warmup_epochs) / (EPOCHS - warmup_epochs-final_epochs)
        alpha = starting_alpha - progress * (starting_alpha - final_alpha)
    else:
        alpha = final_alpha

    return alpha, False


def evaluate_conf_matrix(model_path, learning_rate, alpha):
    logits_model, device, classification_loss_fn, _, p = reset_model(in_channels=3, num_classes=building_classes)

    logits_model.load_state_dict(torch.load(model_path))
    logits_model.to(device)
    logits_model.eval()

    reset_conf_matrices(conf_matrices)
    optimizer = torch.optim.Adam(logits_model.parameters(), lr=learning_rate)

    for batch_elements in train_loader:
        features_param, labels_list = __get_elements_from_batch(batch_elements)

        # Move to device if needed
        features_param = features_param.to(device)
        labels_list = [lbl.to(device) for lbl in labels_list]

        train_step(features_param, *labels_list, optimizer=optimizer, logits_model=logits_model, classification_loss_fn=classification_loss_fn, p=p, alpha=alpha)


    for batch_elements_test in test_loader:
        features_param, labels_list = __get_elements_from_batch(batch_elements_test)

        # Move to device if needed
        features_param = features_param.to(device)
        labels_list = [lbl.to(device) for lbl in labels_list]

        test_step(features_param, *labels_list, logits_model=logits_model, classification_loss_fn=classification_loss_fn, p=p, alpha=alpha)

    
    #print_conf_matrices(conf_matrices)

def run_consistency_validation(model_path, output_csv_path, raw_output_csv_path, output_lp_path, txt_file, lp_to_run="rules.lp", sample_loader=test_loader, debug_mode=False):
    
    model_mode= False #CNN model in eval mode. if its in train mode, the dropout layers mess up the results bc they have different values

    print("\n generating clingo rules \n")
    new_lp_file = open(lp_to_run, "w+")
    test_new_rules.generate_clingo_rules(rules_and_concepts.get_all_axioms(), new_lp_file, debug_mode=debug_mode)
    new_lp_file.close()


    print("\n starting testing \n")
    logits_model, device, p = export_predictions_to_csv_and_lp(model_path, output_csv_path, raw_output_csv_path, output_lp_path, sample_loader=sample_loader)

    clingo_output, clingo_stederr = run_clingo(output_lp_path, lp_to_run=lp_to_run)
    print(f" clingo_stderr {clingo_stederr}")
    output, clingo_output_per_sample = compute_consistency_per_rule(clingo_output, txt_file)

    ltn_output_per_sample, comparison_per_rule, disagreement_values = axioms.evaluate_per_sample_axioms(logits_model, sample_loader, p, device, clingo_output_per_sample)


    #comparison_per_rule = compare_ltn_vs_clingo(ltn_output_per_sample, clingo_output_per_sample)

    print(f"clingo ou per sample {clingo_output_per_sample}\n")
    print(f"consistency results: {output}\n" )
    print(f"disagreeement values: {disagreement_values}\n")

    return clingo_output_per_sample, ltn_output_per_sample, comparison_per_rule, disagreement_values


def compare_ltn_vs_clingo(ltn_per_sample, clingo_per_sample, raw_ltn_output_per_sample, x):
    per_rule = defaultdict(lambda: {"agree": 0, "disagree": 0, "missing": 0})
    #raw_axiom_values = defaultdict(lambda: {"concepts": {}, "final_result": 0.0})

    disagreement_values = {} #key = rule_name
    for sid, ltn_rules in ltn_per_sample.items():
        
        clingo_rules = clingo_per_sample.get(sid, {})
        rule_disagreements = {} #key = sid

        for rule_name, ltn_val in ltn_rules.items():
            if rule_name not in clingo_rules:
                per_rule[rule_name]["missing"] += 1
                continue
            if ltn_val == clingo_rules[rule_name]:
                per_rule[rule_name]["agree"] += 1
            else:
                per_rule[rule_name]["disagree"] += 1
                raw_axiom_values = axioms.recover_axiom_values(rule_name, sid, raw_ltn_output_per_sample, x)
                rule_disagreements[sid] = raw_axiom_values
        
        disagreement_values[rule_name] = rule_disagreements


    return per_rule, disagreement_values


def ensure_run_name_is_valid(run_name):

    experiment_dir = Path("outputs") / run_name

    if not experiment_dir.exists():
        return  run_name # brand new name, nothing to check
    # if every sub-run under this name is already DONE, this name is "used up"
    sub_run_dirs = [d for d in experiment_dir.iterdir() if d.is_dir()]
    if sub_run_dirs and all((d / "DONE").exists() for d in sub_run_dirs):
        raise ValueError(
            f"RUN_NAME '{RUN_NAME}' already has a completed experiment at {experiment_dir}. "
            f"Pick a new RUN_NAME, or delete that folder if you meant to overwrite it."
        )
    else:
        return run_name
    
    # otherwise: folder exists but has an unfinished run (no DONE yet) -> treat as resume, allow it



""" SCRIPT """
LIMIT = constants.LIMIT
EPOCHS = constants.EPOCHS #isto serve para definir quao gradualmente o alpha é modeficado, 150 era fixe para o conhecimento original

#EARLY_STOPPING_DELTA = 0.005
PATIENCE = constants.PATIENCE
patience_multiplier = 1
if TRAIN_WITH_A_SUBSET: 
    patience_multiplier = LEN_TRAIN_DATASET / SUBSET_SIZE
    print(f"FINAL PATIENCE: {PATIENCE*patience_multiplier}") 


MODEL_SAVING_INTERVAL = constants.MODEL_SAVING_INTERVAL
LEARNING_RATE= constants.LEARNING_RATE
output_dir = ""

#metrics_dict.update(class_train_accuracy_metric)

def train_loop(warmup_epochs = 10, final_alpha = 0.25, final_epochs=30, starting_alpha=1.0, patience=20, early_stopping_delta=0.001, learning_rate=0.001, train_model_number=0, seed=None):
    #reset model
    logits_model, device, classification_loss_fn, super_loss_fn, p = reset_model(in_channels=3, num_classes=building_classes, seed=seed)
    debug_batch_alignment(train_loader, logits_model, device)

    #folder
    ensure_run_name_is_valid(run_name=RUN_NAME) #<-- crash if invalid name

    output_dir = "outputs" / Path(f"{RUN_NAME}") #_outputs{train_model_number}
    output_dir.mkdir(parents=True, exist_ok=True)

    output_dir = output_dir / Path(f"run{train_model_number}_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = output_dir / "checkpoint.pth"
    done_marker = output_dir / "DONE"


    csv_path = output_dir / "metrics.csv"
    satAxiom_csv_path = output_dir / "sat_level_per_axiom.csv"
    predictions_csv_path = output_dir / "threshould_predictions_val.csv"
    predictions_csv_path_train = output_dir / "threshould_predictions_train.csv"
    raw_predictions_csv_path = output_dir / "raw_predictions_val.csv"
    raw_predictions_csv_path_train = output_dir / "raw_predictions_train.csv"
    output_lp_path = output_dir / "predictions_val.lp"
    output_lp_path_train = output_dir / "predictions_train.lp"
    txt_path = output_dir / "stats.txt"
    consistency_validation_path = output_dir / "consistency_validation_val.txt"
    consistency_validation_path_train = output_dir / "consistency_validation_train.txt"
    conf_matrix_path = output_dir / "conf_matrix.txt"
    txt_path_final_results = output_dir / "best_epoch_results.txt"
    patience_tracker_path = output_dir / "patience_tracker.txt"


    optimizer = torch.optim.Adam(logits_model.parameters(), lr=learning_rate)

    best_loss = 10000.0
    best_epoch = -1
    epochs_no_improve = 0
    start_epoch = 0



    if checkpoint_path.exists():
        print(f"[checkpoint] resuming from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        logits_model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        start_epoch = checkpoint["epoch"] + 1
        best_loss = checkpoint["best_loss"]
        best_epoch = checkpoint["best_epoch"]
        epochs_no_improve = checkpoint["epochs_no_improve"]
        torch.set_rng_state(checkpoint["torch_rng_state"])
        np.random.set_state(checkpoint["numpy_rng_state"])
        if torch.cuda.is_available() and checkpoint.get("cuda_rng_state") is not None:
            torch.cuda.set_rng_state_all(checkpoint["cuda_rng_state"])
        print(f"[checkpoint] resuming at epoch {start_epoch}, best_loss={best_loss} from epoch {best_epoch}")


    best_model_path = output_dir / "best_model.pth"
    epochs_completed = 0
    constant_alpha = True

    # scheduled_parameters = defaultdict(lambda: {}) -> This can be used to schedule hyperparameters
    template = "Epoch {}"
    satAxiom_template = "Epoch {}"

    satAxiom_keys = axioms.get_rule_sat_metrics_keys()

    for metrics_label in metrics_dict.keys():
        template += ", %s: {:.5f}" % metrics_label

    if csv_path is not None:
        resuming = csv_path.exists() and csv_path.stat().st_size > 0

        csv_file = open(csv_path, "a" if resuming else "w+")
        headers = ",".join(["Epoch", "Alpha"] + list(metrics_dict.keys())) #sem o alpha
        csv_template = ",".join(["{}" for _ in range(len(metrics_dict) + 2)]) #era +1

        if not resuming:
            csv_file.write(headers + "\n")


    for metrics_label in satAxiom_keys:
        satAxiom_template += ", %s: {:.5f}" % metrics_label

    if satAxiom_csv_path is not None:
        resuming = satAxiom_csv_path.exists() and satAxiom_csv_path.stat().st_size > 0

        satAxiom_csv_file = open(satAxiom_csv_path, "a" if resuming else "w+")
        satAxiom_headers = ",".join(["Epoch", "Alpha"] + list(satAxiom_keys)) #sem o alpha
        satAxiom_csv_template = ",".join(["{}" for _ in range(axioms.get_rule_sat_metrics_len() + 2)]) #era +1

        if not resuming:
            satAxiom_csv_file.write(satAxiom_headers + "\n")

    

    for epoch in range(start_epoch, LIMIT):
        print(f"starting epoch {epoch}")
        reset_conf_matrices(conf_matrices)
        axioms.reset_rule_sat_metrics()
        #reset metrics
        for metrics in metrics_dict.values():
            metrics.reset_state()

        #alpha, constant_alpha = new_calculate_alpha(epoch, warmup_epochs, final_alpha, final_epochs, starting_alpha)
        alpha = starting_alpha
        #alpha = 0.5
        metrics_dict["alpha"].update(alpha)

        print(f"alpha: {alpha}")

        for batch_elements in train_loader:
            features_param, labels_list = __get_elements_from_batch(batch_elements)

            #print("labels list")
            #print(labels_list.shape)

            # Move to device if needed
            features_param = features_param.to(device)
            labels_list = [lbl.to(device) for lbl in labels_list]

            #print("train step")
            train_step(features_param, *labels_list, optimizer=optimizer, logits_model=logits_model, classification_loss_fn=classification_loss_fn, super_loss_fn=super_loss_fn, p=p, alpha=alpha)

        if epoch % VALIDATION_INTERVAL == 0:

            for batch_elements_test in test_loader:
                features_param, labels_list = __get_elements_from_batch(batch_elements_test)

                # Move to device if needed
                features_param = features_param.to(device)
                labels_list = [lbl.to(device) for lbl in labels_list]

                test_step(features_param, *labels_list, logits_model=logits_model, classification_loss_fn=classification_loss_fn, super_loss_fn=super_loss_fn, p=p, alpha=alpha)


            metrics_results = [metrics.result() for metrics in metrics_dict.values()]
            outputs_and_prints.write_to_csv_file(template, csv_template, metrics_results, epoch, alpha, csv_file, csv_path)


            satAxiom_results = axioms.get_rule_sat_metrics_results()
            outputs_and_prints.write_to_csv_file(satAxiom_template, satAxiom_csv_template, satAxiom_results, epoch, alpha, satAxiom_csv_file, csv_path)


            #early stopping condition
            current_loss = metrics_dict["combined_val_loss"].result()
            new_loss = best_loss - early_stopping_delta #preciso de mudar este nome

            print(f"best_loss: {best_loss}, current_loss: {current_loss}, number of no improve runs:{epochs_no_improve}/{patience}")
            patience_tracker_file = open(patience_tracker_path, "w+")
            patience_tracker_file.write(f"best_loss: {best_loss} from epoch {best_epoch}, current_loss: {current_loss} from epoch {epoch}, number of no improve cycles of {VALIDATION_INTERVAL} epochs:{epochs_no_improve}/{patience}\n")
            patience_tracker_file.close()

            if current_loss < new_loss:
                best_loss = current_loss
                best_epoch = epoch
                epochs_no_improve = 0
                torch.save(logits_model.state_dict(), best_model_path)
                print("\n\n\n CHANGED BEST LOSS \n\n\n")
            elif epoch > 0:
                #print("\n\n\n CHANGED BEST SAT \n\n\n")
                epochs_no_improve += 1


        torch.save({
            "epoch": epoch,
            "model_state_dict": logits_model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_loss": best_loss,
            "best_epoch": best_epoch,
            "epochs_no_improve": epochs_no_improve,
            "torch_rng_state": torch.get_rng_state(),
            "numpy_rng_state": np.random.get_state(),
            "cuda_rng_state": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
        }, checkpoint_path)

        if epochs_no_improve >= patience:
            print("EARLY STOPPING TRIGGERED")
            epochs_completed = epoch
            break


        #model saving


        #metrics_dict.clear()
        


    print("training finished, starting to save the model")
    txt_file = open(txt_path, "w+")
    txt_file_final_results = open(txt_path_final_results, "w+")
    conf_matrix_file = open(conf_matrix_path, "w+")
    outputs_and_prints.write_results_description_in_txt(txt_file, logits_model, epochs_completed,warmup_epochs, final_epochs, final_alpha, starting_alpha, patience, constant_alpha, subset_class_pos_rates, info_about_dataset, seed, best_epoch, TRAIN_TEST_LIMIT)
    #txt_file.write("\n\n\n\n")
    
    #txt_file.write(subset_class_pos_rates)

    outputs_and_prints.write_conf_matrices_to_file(conf_matrices, conf_matrix_file)

    outputs_and_prints.summarize_best_epoch(csv_path, txt_file_final_results, best_epoch)

    model_path = best_model_path

    #torch.save(logits_model.state_dict(), model_path)

    consistency_validation_file = open(consistency_validation_path, "w+")
    consistency_validation_file_train = open(consistency_validation_path_train, "w+")

    _, _, clingo_ltn_comparison, disagreement_values = run_consistency_validation(model_path, predictions_csv_path, raw_predictions_csv_path, output_lp_path, consistency_validation_file, lp_to_run="utils/rules.lp", sample_loader=test_loader)
    outputs_and_prints.summarize_best_epoch_sat_metrics(satAxiom_csv_path, consistency_validation_file, clingo_ltn_comparison, disagreement_values, best_epoch)

    _, _, clingo_ltn_comparison_train, disagreement_values_train = run_consistency_validation(model_path, predictions_csv_path_train, raw_predictions_csv_path_train, output_lp_path_train, consistency_validation_file_train, lp_to_run="utils/rules.lp", sample_loader=train_loader)
    outputs_and_prints.summarize_best_epoch_sat_metrics(satAxiom_csv_path, consistency_validation_file_train, clingo_ltn_comparison_train, disagreement_values_train, best_epoch)

    done_marker.write_text("done")
    checkpoint_path.unlink(missing_ok=True)  # optional: no longer needed once finished

    if csv_path is not None:
        csv_file.close()
        satAxiom_csv_file.close()

        txt_file.close()
        txt_file_final_results.close()
        conf_matrix_file.close()
        consistency_validation_file.close()

    #default 0.7, 0.8, 0.9

ensure_run_name_is_valid(run_name=RUN_NAME) #<-- crash if invalid name
 
for i in range(0,2):
    run_output_dir = Path("outputs") / Path(RUN_NAME) / f"run{i}_outputs"

    if (run_output_dir / "DONE").exists():
        print(f"Run {i} already completed, skipping")
        continue

    seed_path = run_output_dir / "seed.txt"
    if seed_path.exists():
        seed = int(seed_path.read_text().strip())
        print(f"Run {i}: resuming with existing seed {seed}")
    else:
        seed = torch.randint(0, 100000, (1,)).item()
        run_output_dir.mkdir(parents=True, exist_ok=True)
        seed_path.write_text(str(seed))
        print(f"Run {i}: new seed {seed}")


    starting_alpha = 1.0
    if i== 0:
        starting_alpha = 1.0
    if i ==1:
        starting_alpha = 0.5
    if i ==2:
        starting_alpha = 0.1
    if i ==3:
        starting_alpha = 0.0

    patience = PATIENCE*patience_multiplier/VALIDATION_INTERVAL

    train_loop(warmup_epochs = 10, final_alpha = 0.25, final_epochs=30, starting_alpha= starting_alpha, patience=patience, early_stopping_delta=0.005, learning_rate=LEARNING_RATE, train_model_number=i, seed=seed)





    