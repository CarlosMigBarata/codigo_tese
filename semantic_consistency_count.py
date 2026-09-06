import re, subprocess, sys
from pathlib import Path

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

def semantic_consistency_train(run_dir, rules="newRules.lp", n_val=4000):
    facts = Path(run_dir) / "predictions_train.lp"
    out = subprocess.run(
        ["clingo", rules, str(facts), "--outf=0"],
        capture_output=True, text=True, timeout=600,
    ).stdout
    bad = set()
    for atom in re.findall(r"rule_not_holds\((\w+),", out):
        bad.add(atom)
    bad.discard("sample_id")          # stray fact in newRules.lp, see note
    return 1 - len(bad) / n_val, len(bad)

if __name__ == "__main__":
    score_val, n_val = semantic_consistency_val(sys.argv[1])
    score_train, n_train = semantic_consistency_train(sys.argv[1])

    print(f"{n_val} samples violate >=1 axiom -> semantic consistency = {score_val:.4f}")
    print(f"{n_train} samples violate >=1 axiom -> semantic consistency = {score_train:.4f}")