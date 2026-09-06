import pandas as pd

def check_conditions(csv_path):
    df = pd.read_csv(csv_path)

    conditions = {
        "Residential": 1,
        "Truck": 1,
        "Sign":1,
    }

    mask = pd.Series(True, index=df.index)
    for col, val in conditions.items():
        mask &= (df[col] == val)

    matches = df[mask]

    if not matches.empty:
        print(f"Found {len(matches)} matching row(s):")
        print(matches)
    else:
        print("No matching rows found.")

    return matches


if __name__ == "__main__":
    check_conditions("/home/sofia/Desktop/datasets/datasetVCB/all.csv")