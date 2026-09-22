import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd


# USAGE
# Works directly off the correlation CSVs produced by neuron_concept_correlation.py --
# no model checkpoint or GPU needed.
# python3 greedy_neuron_matching.py zzz_data_evaluation/onlyEquiv_neuron_concept_correlation/concept_neuron_correlation_alpha0.8.csv --latex
#
# Multiple files at once:
# python3 greedy_neuron_matching.py zzz_data_evaluation/onlyEquiv_neuron_concept_correlation/*.csv --latex


def load_matrix(path):
    df = pd.read_csv(path, index_col=0)
    names = list(df.columns)
    matrix = df.to_numpy()  # [pool_size, num_labels]
    return names, matrix


def designated_r(matrix, names):
    """neuron i (i < num_labels, the real readout slice) -> label i, as always used in practice."""
    return {name: matrix[i, i] for i, name in enumerate(names)}


def greedy_matching(matrix, names):
    """
    Greedy maximum-weight bipartite matching: repeatedly take the highest-|r|
    (neuron, label) pair whose neuron and label are both still unclaimed, until
    every label has a distinct neuron. This is the "oracle ceiling" -- the best
    one-to-one assignment achievable from this layer, unconstrained by the
    axiom's fixed index mapping.
    """
    pool_size, num_labels = matrix.shape
    triples = sorted(
        ((abs(matrix[i, j]), i, j) for i in range(pool_size) for j in range(num_labels)),
        key=lambda t: t[0], reverse=True,
    )

    used_neurons = set()
    assigned = {}  # label_idx -> neuron_idx
    for _, i, j in triples:
        if i in used_neurons or j in assigned:
            continue
        assigned[j] = i
        used_neurons.add(i)
        if len(assigned) == num_labels:
            break

    greedy_r = {names[j]: matrix[i, j] for j, i in assigned.items()}
    greedy_neuron = {names[j]: i for j, i in assigned.items()}
    return greedy_r, greedy_neuron


def random_r_stats(matrix, names, trials, rng):
    """
    Random-injective-mapping baseline, computed directly on the correlation
    matrix (cheap: no model pass, so a large trial count is free).
    """
    pool_size, num_labels = matrix.shape
    pool = list(range(pool_size))
    trial_values = {name: [] for name in names}

    for _ in range(trials):
        drawn = rng.sample(pool, num_labels)
        for j, name in enumerate(names):
            trial_values[name].append(matrix[drawn[j], j])

    means = {name: float(np.mean(trial_values[name])) for name in names}
    stds = {name: float(np.std(trial_values[name])) for name in names}
    return means, stds


def print_table(names, designated, greedy, greedy_neuron, random_mean, random_std, group_label, latex):
    print(f"\n=== {group_label} ===")
    header = f"{'Name':<20}{'Designated r':>14}{'Greedy r':>12}{'Greedy neuron':>15}{'Random mean r':>16}{'Random std r':>14}"
    print(header)
    for name in names:
        print(f"{name:<20}{designated[name]:>14.3f}{greedy[name]:>12.3f}{greedy_neuron[name]:>15}"
              f"{random_mean[name]:>16.3f}{random_std[name]:>14.3f}")

    if latex:
        print(r"\begin{table}[htbp]")
        print(r"\centering")
        print(r"\begin{tabular}{lcccc}")
        print(r"\hline")
        print(rf"\textbf{{{group_label}}} & \textbf{{Designated $r$}} & \textbf{{Greedy $r$}} & "
              r"\textbf{Greedy neuron} & \textbf{Random mean $r$ (std)} \\")
        print(r"\hline")
        for name in names:
            print(f"{name} & {designated[name]:.3f} & {greedy[name]:.3f} & {greedy_neuron[name]} & "
                  f"{random_mean[name]:.3f} ({random_std[name]:.3f}) \\\\")
        print(r"\hline")
        print(r"\end{tabular}")
        print(r"\caption{REPLACE ME}")
        print(rf"\label{{tab:REPLACE_ME_{group_label.lower().replace(' ', '_')}}}")
        print(r"\end{table}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare designated, greedy-matched, and random neuron selection "
                    "strategies using precomputed neuron-label correlation matrices "
                    "(from neuron_concept_correlation.py)."
    )
    parser.add_argument("correlation_csvs", nargs="+", type=Path,
                         help="One or more building/concept_neuron_correlation_*.csv files.")
    parser.add_argument("--trials", type=int, default=10000,
                         help="Random-permutation trials (default: 10000 -- cheap, no model pass needed).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--latex", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    for csv_path in args.correlation_csvs:
        names, matrix = load_matrix(csv_path)
        group_label = csv_path.stem.replace("_", " ")

        designated = designated_r(matrix, names)
        greedy, greedy_neuron = greedy_matching(matrix, names)
        random_mean, random_std = random_r_stats(matrix, names, args.trials, rng)

        print_table(names, designated, greedy, greedy_neuron, random_mean, random_std, group_label, args.latex)


if __name__ == "__main__":
    main()