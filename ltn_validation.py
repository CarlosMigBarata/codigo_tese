from pathlib import Path

import ltn
import torch



import utils.test_new_rules as test_new_rules
import utils.rules_and_concepts as rules_and_concepts
import utils.axioms as axioms
import dissertation_workplace_script as script

print("\n\n\nfinish imports, starting \n\n\n")

CLASSES = rules_and_concepts.get_all_classes() #era get_classes
ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
building_classes = len(ALL_BUILDING_CLASSES)
concepts = len(ALL_CONCEPTS)


concepts_pos = building_classes + concepts
building_classes = len(ALL_BUILDING_CLASSES)

ltn_path = "z_ltn_check_allConcepts_new"
clingo_path = "z_clingo_check_allConcepts_new"


Path(ltn_path).mkdir(exist_ok=True)
Path(clingo_path).mkdir(exist_ok=True)

# Rules don't change across concepts/modes — generate once.
RULES_LP_PATH = "utils/rules.lp"
with open(RULES_LP_PATH, "w+") as rules_file:
    test_new_rules.generate_clingo_rules(rules_and_concepts.get_all_axioms(), rules_file, debug_mode=False)





print(f"all_cols: {CLASSES[:concepts_pos]}")
logits_model, device, classification_loss_fn, super_loss_fn, p = script.reset_model(in_channels=3, num_classes=building_classes, seed=12345)


for i in range(len(CLASSES[:concepts_pos])):

    for j in range(2):
        
        axioms.reset_rule_sat_metrics()  # ← reset before the loop
        gt_sat_accumulator = []
        changes = 0

        for batch_elements_test in script.test_loader:
            features_param, labels_list = script.__get_elements_from_batch(batch_elements_test)
            labels_list = [lbl.to(device) for lbl in labels_list]

            changes += (labels_list[i] != j).sum().item()
            
            labels_list[i][:] = j
            #print(labels_list[0][0])    

            SCALE = 8.0
            gt_tensor = torch.stack(labels_list, dim=1).float()
            pseudo_logits = gt_tensor * (2 * SCALE) - SCALE

            gt_sat = axioms.compute_axioms(
                pseudo_logits, *labels_list,
                p=p, debug_mode=False, validation_mode=True  # ← validation_mode updates per-axiom metrics
            )
            gt_sat_accumulator.append(gt_sat.item())

            #print(gt_sat_accumulator)

        mean_gt_sat = sum(gt_sat_accumulator) / len(gt_sat_accumulator)

        # per-axiom results, same keys as your CSV
        axiom_keys    = axioms.get_rule_sat_metrics_keys()
        axiom_results = axioms.get_rule_sat_metrics_results()

        with open(f"{ltn_path}/LTN_test_{CLASSES[i]}_{j}.txt", "w+") as out_file:
            out_file.write(f"[SAT CHECK] ground truth mean sat: {mean_gt_sat:.4f}\n\n")
            out_file.write("Per-axiom satisfaction on ground truth:\n")
            for key, val in zip(axiom_keys, axiom_results):
                if "_val_" in key:
                    out_file.write(f"  {key:40s}: {val:.4f}\n")

        with open(f"{ltn_path}/all_results_ground_truths.txt", "a+") as compiled_out_file:
            compiled_out_file.write(f"[SAT CHECK] ground truth mean sat when {CLASSES[i]} is {j}: {mean_gt_sat:.4f} {changes}/4000 changed, \n")

        out_file.close()
        compiled_out_file.close()


        mean_gt_sat_baseline = mean_gt_sat


#print(f"mean sat: {mean_gt_sat:.4f}")
#for key, val in zip(axiom_keys, axiom_results):
#    print(f"  {key:40s}: {val:.4f}")


print("\n\n\n\n finshed baselines, moving to perturbations \n\n\n\n")


concept_start = 0
num_concepts = len(CLASSES[:concepts_pos])

for k in range(num_concepts):
    idx = concept_start + k
    concept_name = CLASSES[idx]

    for mode in ["fix0", "fix1", "invert", "random"]:

        axioms.reset_rule_sat_metrics()
        gt_sat_accumulator = []
        changes = 0
        ltn_inconsistent_sids = set()

        facts_lp_path = f"z_clingo_check/{concept_name}_{mode}.lp"
        facts_file = open(facts_lp_path, "w+")

        for batch_elements_test in script.test_loader:
            ids = batch_elements_test[2]
            features_param, labels_list = script.__get_elements_from_batch(batch_elements_test)
            labels_list = [lbl.to(device) for lbl in labels_list]

            original = labels_list[idx].clone()
            if mode == "fix0":
                labels_list[idx][:] = 0
            elif mode == "fix1":
                labels_list[idx][:] = 1
            elif mode == "invert":
                labels_list[idx][:] = 1 - labels_list[idx]
            elif mode == "random":
                labels_list[idx][:] = torch.randint(0, 2, labels_list[idx].shape, device=device)

            changes += (labels_list[idx] != original).sum().item()

            # ---------- LTN ----------
            SCALE = 8.0
            gt_tensor = torch.stack(labels_list, dim=1).float()
            pseudo_logits = gt_tensor * (2 * SCALE) - SCALE

            gt_sat = axioms.compute_axioms(
                pseudo_logits, *labels_list,
                p=p, debug_mode=False, validation_mode=True
            )
            gt_sat_accumulator.append(gt_sat.item())

            x = ltn.Variable("x", pseudo_logits)
            for rule_name, rule_def in axioms.AXIOMS.items():
                body = axioms.build_axiom(p, x, rule_def["left"], rule_def["right"], rule_def["main_op"])
                violated = (body.value <= 0.5)
                for j in torch.nonzero(violated).flatten().tolist():
                    ltn_inconsistent_sids.add(axioms.make_sid(ids[j]))

            # ---------- clingo facts ----------
            for j in range(len(ids)):
                sid = axioms.make_sid(ids[j])
                facts_file.write(f"sample({sid}).\n")
                facts_file.write(f"holds({sid}, building).\n")
                facts_file.write(f"holds({sid}, feature).\n")
                for col_idx, class_name in enumerate(CLASSES):
                    if int(labels_list[col_idx][j].item()) == 1:
                        facts_file.write(f"holds({sid}, {class_name.lower()}).\n")
                facts_file.write("\n")

        facts_file.close()

        mean_gt_sat = sum(gt_sat_accumulator) / len(gt_sat_accumulator)
        delta = mean_gt_sat - mean_gt_sat_baseline  # from cell 10, unperturbed run

        clingo_output, clingo_stderr = script.run_clingo(facts_lp_path, lp_to_run=RULES_LP_PATH)
        with open(f"{clingo_path}/{concept_name}_{mode}_stats.txt", "w+") as stats_file:
            _, clingo_out_per_sample = script.compute_consistency_per_rule(clingo_output, stats_file)

        clingo_inconsistent_sids = {
            sid for sid, rule_vals in clingo_out_per_sample.items()
            if any(v == 0 for v in rule_vals.values())
        }

        axiom_keys    = axioms.get_rule_sat_metrics_keys()
        axiom_results = axioms.get_rule_sat_metrics_results()
        n_total = len(script.test_loader.dataset)

        with open(f"{ltn_path}/LTN_test_{concept_name}_{mode}.txt", "w+") as out_file:
            out_file.write(f"[SAT CHECK] mean sat: {mean_gt_sat:.4f} (baseline {mean_gt_sat_baseline:.4f}, delta {delta:+.4f})\n")
            out_file.write(f"LTN inconsistent samples: {len(ltn_inconsistent_sids)}/{n_total}\n")
            out_file.write(f"clingo inconsistent samples: {len(clingo_inconsistent_sids)}/{n_total}\n\n")
            for key, val in zip(axiom_keys, axiom_results):
                if "_val_" in key:
                    out_file.write(f"  {key:40s}: {val:.4f}\n")

        with open(f"{ltn_path}/all_results_perturbations.txt", "a+") as compiled_out_file:
            compiled_out_file.write(
                f"[SAT CHECK] {concept_name} {mode}: "
                f"mean_sat={mean_gt_sat:.4f} delta={delta:+.4f} changes={changes} "
                f"ltn_inconsistent={len(ltn_inconsistent_sids)}/{n_total} "
                f"clingo_inconsistent={len(clingo_inconsistent_sids)}/{n_total}\n"
            )