import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---- CONFIG ----
#FOLDER = "outputs0_2026-03-20_00-55-28"
#FOLDER = "outputs0_2026-03-19_12-21-36"
#FOLDER = "outputs0_2026-03-19_04-44-45"
#FOLDER = "outputs0_2026-03-20_12-07-19"
#FOLDER = "outputs0_2026-03-20_20-20-15"
#FOLDER = "outputs0_2026-03-21_01-44-11"

#FOLDER = "outputs0_2026-03-21_13-39-46"
FOLDER = "outputs/outputs0_2026-03-23_19-39-18"

#alpha 0.5
#FOLDER = "outputs0_2026-03-20_15-44-41" 


CSV_PATH = Path(f"{FOLDER}/metrics.csv")  # change to your file
OUTPUT_DIR = Path(f"{FOLDER}/plots")
OUTPUT_DIR.mkdir(exist_ok=True)

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

metrics_to_plot1 = [
        "train_loss",
        "test_loss",
        "train_sat_kb",
        "test_sat_kb",
        "alpha"
    ]

'''
metrics_to_plot2 = [
        "cafe_train_accuracy",
        "hotel_train_accuracy",
        "store_train_accuracy",
        "misccommercial_train_accuracy",
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
'''

metrics_to_plot2 = [
        "cafe_train_accuracy",
        "alpha"
    ]

metrics_to_plot3 = [
        "vendingmachine_train_accuracy",
        "statue_train_accuracy",
        "alpha"
    ]



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

def plot_all_metrics(metrics_to_plot, id):
    # ---- SELECT METRICS ----
    exclude_cols = ["Epoch"]  # you can also exclude "Alpha" if you want
    metrics = [col for col in df.columns if col not in exclude_cols]

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

plot_all_metrics(metrics_to_plot=metrics_to_plot1, id=1)

plot_all_metrics(metrics_to_plot=metrics_to_plot2, id=2)

plot_all_metrics(metrics_to_plot=metrics_to_plot3, id=3)