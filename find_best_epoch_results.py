import pandas as pd
import sys
from pathlib import Path



def main():

    if len(sys.argv) < 3:
        print("USAGE: python3 path/to/dir best_epoch")

    input_dir = Path(sys.argv[1])
    best_epoch = sys.argv[2]
    metrics_path = input_dir / "metrics.csv"


    df = pd.read_csv(metrics_path)
    matches = df[df["Epoch"] == int(best_epoch)]

    alpha = float(matches["Alpha"].item())

    train_sat_kb = float(matches["train_sat_kb"].item())
    val_sat_kb = float(matches["val_sat_kb"].item())

    train_class_loss = float(matches["train_loss"].item())
    val_class_loss = float(matches["val_loss"].item())

    train_combined_loss = float(matches["combined_train_loss"].item())
    val_combined_loss = float(matches["combined_val_loss"].item())

    #0.80 & 0.7126 & 0.7117 & 0.0081 & 0.0155 & 0.0640 & 0.0700 \\

    out_str = f"{alpha:.2f} & {train_sat_kb:.4f} & {val_sat_kb:.4f} & {train_class_loss:.4f} & {val_class_loss:.4f} & {train_combined_loss:.4f} & {val_combined_loss:.4f} \\\\"

    print("string to use for latex:\n")
    print(out_str)






if __name__ == "__main__":
    main()