import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

import utils.axioms as axioms
import utils.occlusion as occlusion


if len(sys.argv) < 3:
    print("Usage: python charter.py <mode> <path>")
    print("Mode 0: print from folder, Usage: python charter.py 0 <path>")
    print("Mode 1: print from to_plot folder, Usage python charter.py 1 <not_used>")
    sys.exit(1)


# ---- CONFIG ----
#FOLDER = "outputs0_2026-03-20_00-55-28"
#FOLDER = "outputs0_2026-03-19_12-21-36"
#FOLDER = "outputs0_2026-03-19_04-44-45"
#FOLDER = "outputs0_2026-03-20_12-07-19"
#FOLDER = "outputs0_2026-03-20_20-20-15"
#FOLDER = "outputs0_2026-03-21_01-44-11"

#FOLDER = "outputs0_2026-03-21_13-39-46"
#FOLDER = "outputs/outputs0_2026-03-23_19-39-18"
folder = "outputs/outputs0_2026-03-24_15-51-04"

def set_folder(out_folder):
    return out_folder


mode = sys.argv[1]
folder = "outputs/to_plot"
print(f"Received path: {folder}, mode : {mode}")

OUTPUT_DIR = Path(f"{folder}/plots")
OUTPUT_DIR.mkdir(exist_ok=True)

metrics_to_plot1 = [
        "train_loss",
        "val_loss",
        "train_sat_kb",
        "val_sat_kb",
        "combined_train_loss",
        "combined_val_loss",
        "alpha"

]
if mode == "0":
    folder = sys.argv[2]

    #alpha 0.5
    #FOLDER = "outputs0_2026-03-20_15-44-41" 


    CSV_PATH = Path(f"{folder}/metrics.csv")  # change to your file





    # ---- LOAD DATA ----
    df = pd.read_csv(CSV_PATH)

    # Make sure Epoch is numeric
    df["Epoch"] = pd.to_numeric(df["Epoch"], errors="coerce")

# ---- FUNCTION TO PLOT ----
def plot_metric(df, metric_name):
    plt.figure()
    plt.plot(df["Epoch"], df[metric_name])
    plt.xlabel("Epoch")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over Epochs")
    plt.grid()

    save_path = OUTPUT_DIR / f"{metric_name}.png"
    plt.savefig(save_path)
    plt.close()

    print(f"Saved: {save_path}")




def plot_all_metrics(metrics_to_plot, id):

    # ---- PLOT ----
    plt.figure()

    for metric in metrics_to_plot:
        values = df[metric]
        #norm_values = (values - values.min()) / (values.max() - values.min() + 1e-8)
        plt.plot(df["Epoch"], values, label=metric)

    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.title("All Metrics over Epochs")
    plt.legend()
    plt.grid()

    # ---- SAVE ----
    save_path = OUTPUT_DIR / f"all_metrics{id}.png"
    plt.savefig(save_path)
    plt.close()

    print(f"Saved: {save_path}")





'''plots acrross runs'''





def collect_final_metrics_from_runs(parent_folder):
    parent = Path(parent_folder)

    results = []

    for subfolder in parent.iterdir():
        if not subfolder.is_dir():
            continue

        csv_path = subfolder / "metrics.csv"

        if not csv_path.exists():
            continue

        df = pd.read_csv(csv_path)

        if len(df) == 0:
            continue

        final_row = df.iloc[-1].copy()
        final_row["run"] = subfolder.name  # keep track of run

        results.append(final_row)

    if len(results) == 0:
        print("No runs found!")
        return None

    return pd.DataFrame(results)

def plot_all_metrics_across_runs(df, metrics_to_plot, id):

    # ---- PLOT ----
    plt.figure(figsize=(20, 10))

    for metric in metrics_to_plot:
        values = df[metric]
        #norm_values = (values - values.min()) / (values.max() - values.min() + 1e-8)
        plt.plot(df["run"], values, label=metric, marker='o')

    plt.xlabel("Run")
    plt.ylabel("Value")
    plt.title("Metrics over Runs, final value per run")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()

    # ---- SAVE ----
    save_path = OUTPUT_DIR / f"all_metrics_per_run{id}.png"
    plt.savefig(save_path)
    plt.close()

    print(f"Saved: {save_path}")


'''

def plot_final_metric_across_runs(df, metric_name):
    plt.figure()

    plt.plot(df["run"], df[metric_name], marker='o')

    plt.xlabel("Run")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} (final value per run)")
    plt.xticks(rotation=45)
    plt.grid()

    save_path = OUTPUT_DIR / f"final_{metric_name}.png"
    plt.savefig(save_path)
    plt.close()

    print(f"Saved: {save_path}")




def plot_all_final_metrics(df, metrics_list):
    for metric in metrics_list:
        if metric in df.columns:
            plot_final_metric_across_runs(df, metric)
        else:
            print(f"Skipping {metric} (not found)")
'''



parent_folder = folder


print("picking modes")


if mode == "0":
    print("starting mode 0")
    class_train_metrics, class_val_metrics, concept_train_metrics, concept_val_metrics = axioms.get_classes_to_plot()

    plot_all_metrics(metrics_to_plot=metrics_to_plot1, id=1)

    plot_all_metrics(metrics_to_plot=class_train_metrics, id=2)

    plot_all_metrics(metrics_to_plot=class_val_metrics, id="2b")

    plot_all_metrics(metrics_to_plot=concept_train_metrics, id=3)

    plot_all_metrics(metrics_to_plot=concept_val_metrics, id="3b")



if mode == "1":

    print("starting mode 1")
    df_final = collect_final_metrics_from_runs(parent_folder)

    if df_final is not None:
        plot_all_metrics_across_runs(df_final, metrics_to_plot1, id="_a")

        class_train_metrics, class_val_metrics, concept_train_metrics, concept_val_metrics = axioms.get_classes_to_plot()

        plot_all_metrics_across_runs(df_final, class_train_metrics, id="_b")
        plot_all_metrics_across_runs(df_final, class_val_metrics, id= "_c")
        plot_all_metrics_across_runs(df_final, concept_train_metrics, id = "_d")
        plot_all_metrics_across_runs(df_final, concept_val_metrics, id="_e")





















'''

def plot_each_metric_individually(metrics_to_plot):

    # ---- SELECT METRICS ----
    # You can customize this list

    # ---- PLOT ALL ----
    for metric in metrics_to_plot:
        if metric in df.columns:
            plot_metric(df, metric)

    # ---- OPTIONAL: PLOT ALL METRICS AUTOMATICALLY ----
    # Uncomment if you want everything except Epoch/Alpha
    """
    for col in df.columns:
        if col not in ["Epoch", "Alpha"]:
            plot_metric(df, col)
    """
completo

metrics_to_plot2 = [
        "cafe_train_accuracy",
        "hotel_train_accuracy",
        "store_train_accuracy",
        "misccommercial_train_accuracy",
        "alpha"
    ]

metrics_to_plot2b = [
        "cafe_test_accuracy",
        "hotel_test_accuracy",
        "store_test_accuracy",
        "misccommercial_test_accuracy",
        "alpha"
    ]

metrics_to_plot3 = [
        "awning_train_accuracy",
        "billboard_train_accuracy",
        "vendingmachine_train_accuracy",
        "statue_train_accuracy",
        "table_train_accuracy",
        "wallsign_train_accuracy",
        "alpha"
    ]

metrics_to_plot3b = [
        "awning_test_accuracy",
        "billboard_test_accuracy",
        "vendingmachine_test_accuracy",
        "statue_test_accuracy",
        "table_test_accuracy",
        "wallsign_test_accuracy",
        "alpha"
    ]

disjunction

metrics_to_plot2 = [
        "cafe_train_accuracy",
        "alpha"
    ]


metrics_to_plot3 = [
        "vendingmachine_train_accuracy",
        "statue_train_accuracy",
        "alpha"
    ]

conjunction

metrics_to_plot2 = [
        "misccommercial_train_accuracy",
        "alpha"
    ]

metrics_to_plot2b = [
        "misccommercial_val_accuracy",
        "alpha"
    ]    

metrics_to_plot3 = [
        "awning_train_accuracy",
        "table_test_accuracy",
        "alpha"
    ]

    
metrics_to_plot3b = [
        ""awning_val_accuracy",,
        "table_val_accuracy",
        "alpha"
    ]

metrics_to_plot2 = [
        "misccommercial_train_accuracy",
        "alpha"
    ]

metrics_to_plot2b = [
        "misccommercial_val_accuracy",
        "alpha"
    ]    

metrics_to_plot3 = [
        "awning_train_accuracy",
        "table_train_accuracy",
        "alpha"
    ]

    
metrics_to_plot3b = [
        "awning_val_accuracy",
        "table_val_accuracy",
        "alpha"
    ]
'''