import argparse
import re
import subprocess
from pathlib import Path

from utils import rules_and_concepts, test_new_rules

#USAGE: python3 compile_semantic_consistency.py path/to/testRun_folder --rules newRules.lp
#python3 compile_semantic_consistency.py path/to/testRun_folder --rules newRules.lp --by-alpha
#python3 compile_semantic_consistency.py testRun_Wide testRun_DSL --arch Wide DSL --plot

ALPHA_RE = re.compile(r"Alpha:\s*([\d.]+)")


def semantic_consistency_val(run_dir, rules="newRules.lp", n_val=4000):
    facts = Path(run_dir) / "predictions_val.lp"
    out = subprocess.run(
        ["clingo", rules, str(facts), "--outf=0"],
        capture_output=True, text=True, timeout=600,
    ).stdout
    bad = set()
    for atom in re.findall(r"rule_not_holds\((\w+),", out):
        bad.add(atom)
    bad.discard("sample_id")          # stray fact in newRules.lp, see note
    return 1 - len(bad) / n_val, len(bad)


def semantic_consistency_train(run_dir, rules="newRules.lp", n_train=16000):
    facts = Path(run_dir) / "predictions_train.lp"
    out = subprocess.run(
        ["clingo", rules, str(facts), "--outf=0"],
        capture_output=True, text=True, timeout=600,
    ).stdout
    bad = set()
    for atom in re.findall(r"rule_not_holds\((\w+),", out):
        bad.add(atom)
    bad.discard("sample_id")          # stray fact in newRules.lp, see note
    return 1 - len(bad) / n_train, len(bad)


def get_alpha(run_dir: Path):
    best_file = run_dir / "best_epoch_results.txt"
    if not best_file.exists():
        return None
    m = ALPHA_RE.search(best_file.read_text())
    return float(m.group(1)) if m else None


def find_run_dirs(root: Path):
    if (root / "predictions_val.lp").exists():
        return [root]
    return sorted(root.glob("run*_outputs"))


def mean(values):
    return sum(values) / len(values) if values else None


def infer_architecture(root: Path) -> str:
    name = root.name
    prefix = "testRun_"
    return name[len(prefix):] if name.startswith(prefix) else name


def print_latex_table(rows, avg_train, avg_val, alpha, arch, caption, label):
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\begin{tabular}{lcc}",
        r"\hline",
        r"\textbf{Run} & \textbf{Train Consistency (\%)} & \textbf{Val Consistency (\%)} \\",
        r"\hline",
    ]
    for name, train_c, val_c in rows:
        train_s = f"{train_c * 100:.2f}" if train_c is not None else "-"
        val_s = f"{val_c * 100:.2f}" if val_c is not None else "-"
        lines.append(f"{alpha} ({arch}) & {train_s} & {val_s} \\\\")
    lines.append(r"\hline")
    avg_train_s = f"{avg_train * 100:.2f}" if avg_train is not None else "-"
    avg_val_s = f"{avg_val * 100:.2f}" if avg_val is not None else "-"
    lines.append(f"{alpha} ({arch}) & {avg_train_s} & {avg_val_s} \\\\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        r"\end{table}",
    ]
    print("\n".join(lines))


def plot_grouped_bar_chart(plot_data, metric_label, output_path, show_all_runs=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    archs = sorted(plot_data.keys())
    alphas = sorted({alpha for rows in plot_data.values() for alpha in rows})

    x = np.arange(len(alphas))
    arch_width = 0.8 / len(archs)
    colors = plt.cm.tab10(np.linspace(0, 1, len(archs)))

    fig, ax = plt.subplots(figsize=(1.5 * len(alphas) + 2, 5))
    for i, arch in enumerate(archs):
        arch_offset = (i - (len(archs) - 1) / 2) * arch_width
        color = colors[i]
        for j, alpha in enumerate(alphas):
            values = plot_data[arch].get(alpha, [])
            if not values:
                continue
            if show_all_runs:
                n = len(values)
                sub_width = arch_width / n
                for k, v in enumerate(values):
                    sub_offset = (k - (n - 1) / 2) * sub_width
                    ax.bar(x[j] + arch_offset + sub_offset, v * 100, sub_width,
                           color=color, label=arch if (j == 0 and k == 0) else None)
            else:
                avg = mean(values)
                bars = ax.bar(x[j] + arch_offset, avg * 100, arch_width,
                               color=color, label=arch if j == 0 else None)
                ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{a:g}" for a in alphas])
    ax.set_xlabel("Alpha")
    ax.set_ylabel(f"{metric_label.capitalize()} consistency (%)")
    ax.set_ylim(0, 100)
    title_suffix = "" if show_all_runs else ""
    ax.set_title(f"Semantic consistency ({metric_label}) by alpha and architecture{title_suffix}")
    ax.legend(title="Architecture")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\nSaved chart to {output_path}")

def set_ontology(ontology):

    match ontology:
        case "CLASSIC_ONTOLOGY":
            
            ALL_AXIOMS = rules_and_concepts.CLASSIC_ONTOLOGY

        case "COMMERCIAL_ONLY":
            ALL_AXIOMS = rules_and_concepts.COMMERCIAL_ONLY

        case "INDUSTRIAL_ONLY":
            ALL_AXIOMS = rules_and_concepts.INDUSTRIAL_ONLY

        case "RESIDENTIAL_ONLY":
            ALL_AXIOMS = rules_and_concepts.RESIDENTIAL_ONLY

        case "BUILDING_TYPES_ONLY":
            print("BUILDING TYPES")
            ALL_AXIOMS = rules_and_concepts.BUILDING_TYPES_ONLY

        case "CONJUNCTIONS_ONLY":
            ALL_AXIOMS = rules_and_concepts.CONJUNCTIONS_ONLY
            print("conj only")

        case "EQUIVALENCES_ONLY":
            ALL_AXIOMS = rules_and_concepts.EQUIVALENCES_ONLY
            print("only eqiEQUIVALENCES_ONLY")


        case "SIMPLE_EQUIVALENCES_AND_CONJUNCTIONS":
            ALL_AXIOMS = rules_and_concepts.SIMPLE_EQUIVALENCES_AND_CONJUNCTIONS

        case _:
            ALL_AXIOMS = rules_and_concepts.CLASSIC_ONTOLOGY


    #print(f"ALL axioms selected: {ALL_AXIOMS}")
    return ALL_AXIOMS



def main():
    parser = argparse.ArgumentParser(
        description="Semantic consistency (train and val) per run in a testRun folder, "
                    "plus the average across runs, printed as LaTeX table(s)."
    )
    parser.add_argument("path", nargs="+", help="One or more testRun folders (each containing "
                                      "run*_outputs), or single run folders.")
    parser.add_argument("--arch", nargs="+", default=None,
                         help="Architecture label for each path, e.g. --arch Wide DSL. "
                              "Required when passing more than one path; optional for a "
                              "single path (defaults to the folder name).")
    parser.add_argument("--ontology", default="constants.activeOntology", help="Ontology to compare the consistency to.")
    #parser.add_argument("--rules", default="newRules.lp", help="Path to the clingo rules file.")
    parser.add_argument("--n-val", type=int, default=4000, help="Number of validation samples.")
    parser.add_argument("--n-train", type=int, default=16000,
                         help="Number of training samples (use a smaller value for "
                              "sample-efficiency / subset runs).")
    parser.add_argument("--by-alpha", action="store_true",
                         help="Print a separate table per alpha value, instead of one "
                              "table averaging all runs together.")
    parser.add_argument("--plot", action="store_true",
                         help="Also render a grouped bar chart (alpha on the x-axis, one "
                              "bar per architecture in each group). Implies --by-alpha.")
    parser.add_argument("--plot-metric", choices=["train", "val"], default="val",
                         help="Which consistency to plot.")
    parser.add_argument("--plot-output", default="semantic_consistency_by_alpha.png",
                         help="Filename for the chart (only used with --plot).")
    parser.add_argument("--plot-all-runs", action="store_true",
                         help="Plot every individual run as its own bar instead of "
                              "averaging runs within each (architecture, alpha) group.")
    
    args = parser.parse_args()

    roots = [Path(p) for p in args.path]

    if args.arch is None:
        if len(roots) > 1:
            parser.error("--arch is required when passing more than one path")
        arch_labels = [infer_architecture(roots[0])]
    else:
        if len(args.arch) != len(roots):
            parser.error("--arch must list exactly one label per path")
        arch_labels = args.arch

    if args.plot:
        args.by_alpha = True

    print("\n generating clingo rules \n")
    new_lp_file_name = "temporaryRules.lp"
    new_lp_file = open(new_lp_file_name, "w+")
    print(f"ontology: {args.ontology}")
    ALL_AXIOMS = set_ontology(args.ontology)
    test_new_rules.generate_active_clingo_rules(ALL_AXIOMS, new_lp_file, debug_mode=False)
    new_lp_file.close()

    plot_data = {}          # arch -> alpha -> [consistency values]
    by_arch_alpha = {}      # (arch, key) -> rows, for the LaTeX tables

    for root, arch in zip(roots, arch_labels):
        run_dirs = find_run_dirs(root)
        if not run_dirs:
            print(f"No run*_outputs (or predictions_val.lp) found under {root}")
            continue

        for run_dir in run_dirs:
            key = "all"
            if args.by_alpha:
                key = get_alpha(run_dir)
                if key is None:
                    print(f"Skipping {run_dir} (no alpha found in best_epoch_results.txt)")
                    continue

            try:
                val_c, n_bad_val = semantic_consistency_val(run_dir, rules=new_lp_file_name, n_val=args.n_val)
                train_c, n_bad_train = semantic_consistency_train(run_dir, rules=new_lp_file_name, n_train=args.n_train)
            except Exception as e:
                print(f"Skipping {run_dir} (error running clingo: {e})")
                continue

            print(f"[{arch}] {run_dir.name}: train consistency={train_c:.4f} ({n_bad_train} violate), "
                  f"val consistency={val_c:.4f} ({n_bad_val} violate)")

            by_arch_alpha.setdefault((arch, key), []).append((run_dir.name, train_c, val_c))

            if args.plot:
                metric_val = val_c if args.plot_metric == "val" else train_c
                plot_data.setdefault(arch, {}).setdefault(key, []).append(metric_val)

    keys = sorted({k for _, k in by_arch_alpha}, reverse=True) if args.by_alpha else ["all"]

    for arch in arch_labels:
        for key in keys:
            rows = by_arch_alpha.get((arch, key), [])
            if not rows:
                continue
            avg_train = mean([r[1] for r in rows])
            avg_val = mean([r[2] for r in rows])

            suffix = f"_{arch}_alpha{key:g}" if args.by_alpha else f"_{arch}"
            alpha_note = f" (alpha={key:g})" if args.by_alpha else ""
            if args.by_alpha:
                print(f"\n=== {arch}, alpha = {key:g} ===")

            print_latex_table(
                rows, avg_train, avg_val, key, arch,
                f"Semantic consistency per run, train and validation{alpha_note} ({arch}).",
                f"tab:semantic_consistency{suffix}",
            )
            print()

    if args.plot:
        plot_grouped_bar_chart(plot_data, args.plot_metric, args.plot_output, show_all_runs=args.plot_all_runs)


if __name__ == "__main__":
    main()