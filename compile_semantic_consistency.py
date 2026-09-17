import argparse
import re
import subprocess
from pathlib import Path

from utils import rules_and_concepts, test_new_rules

#USAGE: python3 compile_semantic_consistency.py path/to/testRun_folder --rules newRules.lp
#python3 compile_semantic_consistency.py path/to/testRun_folder --rules newRules.lp --by-alpha

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


def print_latex_table(rows, avg_train, avg_val, alpha, caption, label):
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
        lines.append(f"{alpha} (DSL) & {train_s} & {val_s} \\\\")
    lines.append(r"\hline")
    avg_train_s = f"{avg_train * 100:.2f}" if avg_train is not None else "-"
    avg_val_s = f"{avg_val * 100:.2f}" if avg_val is not None else "-"
    #lines.append(f"\\textbf{{Average}} & {avg_train_s} & {avg_val_s} \\\\")
    lines.append(f"{alpha} (DSL) & {avg_train_s} & {avg_val_s} \\\\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        r"\end{table}",
    ]
    print("\n".join(lines))


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

        case "EQUIVALENCES_ONLY":
            ALL_AXIOMS = rules_and_concepts.EQUIVALENCES_ONLY

        case "SIMPLE_EQUIVALENCES_AND_CONJUNCTIONS":
            ALL_AXIOMS = rules_and_concepts.SIMPLE_EQUIVALENCES_AND_CONJUNCTIONS

        case _:
            ALL_AXIOMS = rules_and_concepts.CLASSIC_ONTOLOGY

    return ALL_AXIOMS



def main():
    parser = argparse.ArgumentParser(
        description="Semantic consistency (train and val) per run in a testRun folder, "
                    "plus the average across runs, printed as LaTeX table(s)."
    )
    parser.add_argument("path", help="A testRun folder (containing run*_outputs), or a "
                                      "single run folder.")
    parser.add_argument("--ontology", default="constants.activeOntology", help="Ontology to compare the consistency to.")
    #parser.add_argument("--rules", default="newRules.lp", help="Path to the clingo rules file.")
    parser.add_argument("--n-val", type=int, default=4000, help="Number of validation samples.")
    parser.add_argument("--n-train", type=int, default=16000,
                         help="Number of training samples (use a smaller value for "
                              "sample-efficiency / subset runs).")
    parser.add_argument("--by-alpha", action="store_true",
                         help="Print a separate table per alpha value, instead of one "
                              "table averaging all runs together.")
    args = parser.parse_args()

    root = Path(args.path)
    run_dirs = find_run_dirs(root)
    if not run_dirs:
        print(f"No run*_outputs (or predictions_val.lp) found under {root}")
        return

    print("\n generating clingo rules \n")
    new_lp_file_name = "temporaryRules.lp"
    new_lp_file = open(new_lp_file_name, "w+")
    print(f"ontology: {args.ontology}")
    ALL_AXIOMS = set_ontology(args.ontology)
    test_new_rules.generate_active_clingo_rules(ALL_AXIOMS, new_lp_file, debug_mode=False)
    new_lp_file.close()


    by_alpha = {}
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

        print(f"{run_dir.name}: train consistency={train_c:.4f} ({n_bad_train} violate), "
              f"val consistency={val_c:.4f} ({n_bad_val} violate)")

        by_alpha.setdefault(key, []).append((run_dir.name, train_c, val_c))

    keys = sorted(by_alpha.keys(), reverse=True) if args.by_alpha else ["all"]

    for key in keys:
        rows = by_alpha.get(key, [])
        if not rows:
            continue
        avg_train = mean([r[1] for r in rows])
        avg_val = mean([r[2] for r in rows])

        suffix = f"_alpha{key:g}" if args.by_alpha else ""
        alpha_note = f" (alpha={key:g})" if args.by_alpha else ""
        if args.by_alpha:
            print(f"\n=== alpha = {key:g} ===")

        alpha = key

        print_latex_table(
            rows, avg_train, avg_val, alpha,
            f"Semantic consistency per run, train and validation{alpha_note}.",
            f"tab:semantic_consistency{suffix}",
        )
        print()


if __name__ == "__main__":
    main()
