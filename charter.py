import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import re

import utils.axioms as axioms
import utils.occlusion as occlusion


if len(sys.argv) < 3:
    print("Usage: python charter.py <mode> <path>")
    print("Mode 0: print from folder, Usage: python charter.py 0 <path>")
    print("Mode 1: print from to_plot folder, Usage python charter.py 1 <not_used>")
    print("Mode 2: compile best-epoch metrics + rule consistency from to_plot folder, Usage python charter.py 2 <not_used>")
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
folder = "outputs/_to_plot"
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
metrics_to_plot1_old = [
        "train_loss",
        "test_loss",
        "train_sat_kb",
        "test_sat_kb",
        "combined_train_loss",
        "combined_test_loss",
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
    plt.figure(figsize=(25, 15))

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


'''collect at best epoch instead of final epoch'''
_PATIENCE_TRACKER_RE = re.compile(r"best_loss:\s*[\d.eE+-]+\s*from epoch\s*(?P<best_epoch>\d+)")


def read_best_epoch(run_folder, patience_filename="patience_tracker.txt"):
    """Read the epoch a run actually converged on, straight from patience_tracker.txt
    (written every validation cycle in train_loop, so it's available even for runs
    still in progress). Recomputing this as a raw min over metrics.csv's loss column
    does NOT match: early stopping in train_loop only accepts a new best once it beats
    the previous one by early_stopping_delta, so a later epoch can have a numerically
    lower loss without being the epoch best_model.pth was actually checkpointed from.
    """
    patience_path = Path(run_folder) / patience_filename

    if not patience_path.exists():
        return None

    m = _PATIENCE_TRACKER_RE.search(patience_path.read_text())
    return int(m["best_epoch"]) if m else None


def collect_best_epoch_metrics_from_runs(parent_folder, csv_filename="metrics.csv"):
    """Like collect_final_metrics_from_runs, but takes the row at each run's best
    epoch (per read_best_epoch) instead of the last logged row. The last logged row
    is recorded after early-stopping patience has already run out, so it undersells
    the run compared to the checkpoint that was actually kept as best_model.pth.
    """
    parent = Path(parent_folder)

    results = []

    for subfolder in sorted(parent.iterdir()):
        if not subfolder.is_dir():
            continue

        csv_path = subfolder / csv_filename

        if not csv_path.exists():
            continue

        best_epoch = read_best_epoch(subfolder)

        if best_epoch is None:
            continue

        run_df = pd.read_csv(csv_path)
        matching_rows = run_df[run_df["Epoch"] == best_epoch]

        if matching_rows.empty:
            continue

        best_row = matching_rows.iloc[0].copy()
        best_row["run"] = subfolder.name

        results.append(best_row)

    if len(results) == 0:
        print("No runs found!")
        return None

    return pd.DataFrame(results)


def collect_best_epoch_axiom_metrics_from_runs(parent_folder, axiom_filename="sat_level_per_axiom.csv"):
    """Same idea as collect_best_epoch_metrics_from_runs, but for
    sat_level_per_axiom.csv - it's logged at the same epochs as metrics.csv, so the
    same best_epoch (from read_best_epoch) picks out the matching row.
    """
    parent = Path(parent_folder)

    results = []

    for subfolder in sorted(parent.iterdir()):
        if not subfolder.is_dir():
            continue

        axiom_path = subfolder / axiom_filename

        if not axiom_path.exists():
            continue

        best_epoch = read_best_epoch(subfolder)

        if best_epoch is None:
            continue

        run_axiom_df = pd.read_csv(axiom_path)
        matching_rows = run_axiom_df[run_axiom_df["Epoch"] == best_epoch]

        if matching_rows.empty:
            continue

        best_row = matching_rows.iloc[0].copy()
        best_row["run"] = subfolder.name

        results.append(best_row)

    if len(results) == 0:
        print("No runs found!")
        return None

    return pd.DataFrame(results)


def get_axiom_metrics_to_plot():
    """Mirrors axioms.get_classes_to_plot(), but for the per-axiom satisfaction
    columns logged in sat_level_per_axiom.csv (rule_sat_metrics), split into
    train/val lists.
    """
    axiom_train_metrics = []
    axiom_val_metrics = []

    for key in axioms.get_rule_sat_metrics_keys():
        if key.endswith("_train_accuracy"):
            axiom_train_metrics.append(key)
        elif key.endswith("_val_accuracy"):
            axiom_val_metrics.append(key)

    axiom_train_metrics.append("Alpha")
    axiom_val_metrics.append("Alpha")

    return axiom_train_metrics, axiom_val_metrics


'''parse the unstructured consistency_validation_*.txt files'''
_CONSISTENCY_LINE_RE = re.compile(
    r"^(?P<rule>\S+)\s*\|\s*consistency=(?P<consistency>-?[\d.]+)\s*\|\s*"
    r"rule_holds=(?P<rule_holds>\d+)\s*\|\s*rule_vac_holds=(?P<rule_vac_holds>\d+)\s*\|\s*"
    r"violations=(?P<violations>\d+)\s*\|\s*total=(?P<total>\d+)"
)
_AGREEMENT_LINE_RE = re.compile(r"^(?P<rule>\S+)\s*:\s*\{(?P<body>[^}]*)\}")


def parse_consistency_validation_file(txt_path):
    """Parse a consistency_validation_*.txt file into a DataFrame indexed by rule
    name, combining the 'CONSISTENCY PER RULE' block (Clingo-side) and the
    'LTN vs Clingo agreement per axiom' block. Skips the per-sample disagreement
    listing further down the file - that's case-study detail, not summary data.
    """
    consistency_rows = {}
    agreement_rows = {}
    section = None

    with open(txt_path) as f:
        for line in f:
            stripped = line.strip()

            if stripped.startswith("========="):
                if "CONSISTENCY PER RULE" in stripped.upper().replace("CONISTENCY", "CONSISTENCY"):
                    section = "consistency"
                elif "LTN vs Clingo" in stripped:
                    section = "agreement_header"
                else:
                    section = None
                continue

            if section == "consistency":
                m = _CONSISTENCY_LINE_RE.match(stripped)
                if m:
                    # keyed lower-case: the agreement block below lowercases rule
                    # names while this block keeps the axiom's original casing
                    consistency_rows[m["rule"].lower()] = {
                        "display_name": m["rule"],
                        "consistency": float(m["consistency"]),
                        "rule_holds": int(m["rule_holds"]),
                        "rule_vac_holds": int(m["rule_vac_holds"]),
                        "violations": int(m["violations"]),
                        "total": int(m["total"]),
                    }

            elif section == "agreement_header":
                if stripped == "agreement per axiom":
                    section = "agreement"
                continue

            elif section == "agreement":
                if stripped.startswith("Disagreements between"):
                    section = None
                    continue
                m = _AGREEMENT_LINE_RE.match(stripped)
                if m:
                    counts = {"agree": None, "disagree": None, "missing": None}
                    if m["body"].strip():
                        for key in counts:
                            km = re.search(rf"'{key}':\s*(\d+)", m["body"])
                            if km:
                                counts[key] = int(km.group(1))
                    counts["display_name"] = m["rule"]
                    agreement_rows[m["rule"].lower()] = counts

    rules = sorted(set(consistency_rows) | set(agreement_rows))
    records = []

    for rule in rules:
        c = consistency_rows.get(rule, {})
        a = agreement_rows.get(rule, {})
        display_name = c.get("display_name") or a.get("display_name") or rule

        agree = a.get("agree")
        disagree = a.get("disagree")
        compared = (agree + disagree) if agree is not None and disagree is not None else None

        records.append({
            "rule": display_name,
            "consistency": c.get("consistency"),
            "rule_holds": c.get("rule_holds"),
            "rule_vac_holds": c.get("rule_vac_holds"),
            "violations": c.get("violations"),
            "total": c.get("total"),
            "ltn_agree": agree,
            "ltn_disagree": disagree,
            "ltn_missing": a.get("missing"),
            "ltn_agreement_rate": (agree / compared) if compared else None,
        })

    return pd.DataFrame(records).set_index("rule")


def collect_consistency_across_runs(parent_folder, filename="consistency_validation_val.txt"):
    """Walk every run subfolder, parse its consistency_validation file, and stack
    the results into one long-format DataFrame (columns include 'run' and 'rule')
    suitable for grouped bar charts comparing rule satisfaction across runs.
    """
    parent = Path(parent_folder)
    frames = []

    for subfolder in sorted(parent.iterdir()):
        if not subfolder.is_dir():
            continue

        txt_path = subfolder / filename

        if not txt_path.exists():
            continue

        run_df = parse_consistency_validation_file(txt_path).reset_index()
        run_df["run"] = subfolder.name

        frames.append(run_df)

    if len(frames) == 0:
        print("No consistency files found!")
        return None

    return pd.concat(frames, ignore_index=True)


def plot_rule_metric_across_runs(df_long, metric, id=""):
    """Grouped bar chart of a per-rule metric (e.g. 'consistency' or
    'ltn_agreement_rate') across runs, one bar group per rule.
    """
    pivot = df_long.pivot(index="rule", columns="run", values=metric)

    ax = pivot.plot(kind="bar", figsize=(max(12, len(pivot) * 0.5), 8))
    ax.set_xlabel("Rule")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} per rule, across runs")
    ax.legend(title="Run")
    plt.tight_layout()

    save_path = OUTPUT_DIR / f"{metric}_per_rule{id}.png"
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


if mode == "2":

    print("starting mode 2")
    df_best = collect_best_epoch_metrics_from_runs(parent_folder)

    if df_best is not None:
        plot_all_metrics_across_runs(df_best, metrics_to_plot1, id="_best_a")

        class_train_metrics, class_val_metrics, concept_train_metrics, concept_val_metrics = axioms.get_classes_to_plot()

        plot_all_metrics_across_runs(df_best, class_train_metrics, id="_best_b")
        plot_all_metrics_across_runs(df_best, class_val_metrics, id="_best_c")
        plot_all_metrics_across_runs(df_best, concept_train_metrics, id="_best_d")
        plot_all_metrics_across_runs(df_best, concept_val_metrics, id="_best_e")

    df_axiom_best = collect_best_epoch_axiom_metrics_from_runs(parent_folder)

    if df_axiom_best is not None:
        axiom_train_metrics, axiom_val_metrics = get_axiom_metrics_to_plot()

        plot_all_metrics_across_runs(df_axiom_best, axiom_train_metrics, id="_best_axiom_train")
        plot_all_metrics_across_runs(df_axiom_best, axiom_val_metrics, id="_best_axiom_val")

    df_consistency_val = collect_consistency_across_runs(parent_folder, filename="consistency_validation_val.txt")

    if df_consistency_val is not None:
        plot_rule_metric_across_runs(df_consistency_val, "consistency", id="_val")
        plot_rule_metric_across_runs(df_consistency_val, "ltn_agreement_rate", id="_val")




















