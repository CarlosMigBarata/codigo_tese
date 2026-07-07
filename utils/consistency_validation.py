



import numpy as np
import torch




def export_predictions_to_csv_and_lp(model_path, output_csv_path, raw_output_csv_path, output_lp_path, sample_loader=test_loader):

    logits_model, device, _, p = reset_model(in_channels=3, num_classes=final_classes)

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