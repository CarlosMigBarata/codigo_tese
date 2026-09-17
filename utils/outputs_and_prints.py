import pandas as pd

import utils.constants as constants
import utils.rules_and_concepts as rules_and_concepts
import utils.axioms as axioms


CLASSES = rules_and_concepts.get_all_classes() #era get_classes
ALL_EXISTING_CLASSES = rules_and_concepts.get_all_classes()
ALL_CONCEPTS = rules_and_concepts.get_ALL_CONCEPTS()
ALL_BUILDING_CLASSES = rules_and_concepts.get_all_building_classes()
#final_classes = len(rules_and_concepts.get_all_building_classes())

building_classes = len(ALL_BUILDING_CLASSES)
super_classes = len(rules_and_concepts.get_super_classes())
concepts = len(ALL_CONCEPTS)


concepts_pos = building_classes + concepts
super_classes_pos = concepts_pos + super_classes




'''OUTPUTS'''
def write_results_description_in_txt(txt_file, model, epochs_completed, warmup_epochs, final_epochs, final_alpha, starting_alpha, patience, constant_alpha, subset_class_pos_rates, info_about_dataset, seed, best_epoch, train_test_limit):
    txt_file.write("Results Description\n")
    txt_file.write(f"Seed: {seed}\n")
    txt_file.write("Number of examples: %d\n" % constants.TOTAL_EXAMPLES)
    txt_file.write("Train/Test limit: %d\n" % train_test_limit)
    txt_file.write(f"Validation Interval: {constants.VALIDATION_INTERVAL}\n")
    txt_file.write("Complexity of the Dataset: %d\n" % constants.COMPLEXITY_DATASET)
    txt_file.write("Batch size: %d\n" % constants.BATCH_SIZE)
    txt_file.write("Learning rate: %.5f\n" % constants.LEARNING_RATE)
    txt_file.write(f"trained with building predicates: {constants.BUILDING_PREDICATES}; trained with concept predicates: {constants.CONCEPT_PREDICATES}\n")
    if constants.TRAIN_WITH_A_SUBSET: txt_file.write(info_about_dataset)
    txt_file.write("\n")

    txt_file.write(f"Number of epochs completed: {epochs_completed}/{constants.LIMIT}\n")
    txt_file.write(f"Best epoch found: {best_epoch}\n")
    txt_file.write(f"constant_alpha: {constant_alpha};  patience: {patience} cycles\n")
    if not constant_alpha: txt_file.write(f"staring alpha:{starting_alpha}; final alpha: {final_alpha};\n")
    txt_file.write("\n\n")

    txt_file.write(f"[DEBUG] CLASSES order: {CLASSES}\n")
    txt_file.write(f"[DEBUG] Building classes (first {building_classes}): {CLASSES[:building_classes]}\n")
    txt_file.write(f"[DEBUG] Concepts (from {building_classes} to {concepts_pos}): {CLASSES[building_classes:concepts_pos]}\n")
    txt_file.write(f"[DEBUG] Super classes (after): {CLASSES[concepts_pos:]}\n\n")

    if model is not None:
        txt_file.write("\nModel Architecture:\n")
        txt_file.write(str(model))
        txt_file.write("\n\n")

    if starting_alpha < 1.0:
        txt_file.write(f"ACTIVE ONTOLOGY: {constants.active_ontology}\n")
        rules_and_concepts.write_active_axioms(txt_file)

    if constants.TRAIN_WITH_A_SUBSET:
        txt_file.write("\n\n\n\n")
        txt_file.write(f"[subset] class positive rates:\n")
        txt_file.write(subset_class_pos_rates)



def positive_rate_stats(cm):
    tn, fp, fn, tp = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]
    total = tn + fp + fn + tp
    predicted_positive_rate = (fp + tp) *100 / total
    actual_positive_rate = (fn + tp)*100 / total
    bias = predicted_positive_rate - actual_positive_rate

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall *100 / (precision + recall) if (precision + recall) else 0

    precision = precision *100
    recall = recall *100

    return predicted_positive_rate, actual_positive_rate, bias, precision, recall, f1


def write_conf_matrices_to_file(conf_matrices, txt_file):

    txt_file.write("------------ FORMATO DA MATRIZ --------")
    txt_file.write("\n")
    txt_file.write("----------------[TN, FP]------------------\n")
    txt_file.write("----------------[FN, TP]------------------\n")
    txt_file.write("\n")
    txt_file.write("TN: predicted Negative, Reality Negative\n")
    txt_file.write("FN: predicted Negative, Reality Positive\n")
    txt_file.write("FP: predicted Positive, Reality Negative\n")
    txt_file.write("TP: predicted Positive, Reality Positive\n")
    txt_file.write("\n")
    txt_file.write("------------ METRICAS --------")
    txt_file.write("\n")
    txt_file.write("precision: TP / (TP + FP) \n")
    txt_file.write("recall: TP / (TP + FN) \n")
    txt_file.write("f1: 2 * precision * recall / (precision + recall) \n")
    txt_file.write("\n\n\n")
    

    high_bias = {}
    high_bias_threshould, low_bias_threshould = 20, -20
    for key, cm in conf_matrices.items():
        print(f"{key} confusion matrix:\n{cm}\n")
        txt_file.write(f"{key} confusion matrix:\n{cm}\n")
        predicted_pos_rate, actual_pos_rate, bias, precision, recall, f1 = positive_rate_stats(cm)
        txt_file.write(f"predicted positive: {predicted_pos_rate:.3f}% | actual positive: {actual_pos_rate:.3f}% | bias: {bias:.3f}%\n")
        txt_file.write(f"precision: {precision:.3f}% | recall: {recall:.3f}% | f1: {f1:.3f}%\n\n\n")

        if bias > high_bias_threshould or bias < low_bias_threshould:
            high_bias[key] = cm

    txt_file.write("\n\n\n")
    txt_file.write("------------ HIGH BIAS METRICS --------------------------------------------------------------\n")
    for key, cm in high_bias.items():
        txt_file.write(f"{key} confusion matrix:\n{cm}\n")
        predicted_pos_rate, actual_pos_rate, bias, precision, recall, f1 = positive_rate_stats(cm)
        txt_file.write(f"predicted positive: {predicted_pos_rate:.3f}% | actual positive: {actual_pos_rate:.3f}% | bias: {bias:.3f}%\n")
        txt_file.write(f"precision: {precision:.3f}% | recall: {recall:.3f}% | f1: {f1:.3f}%\n\n\n")


def summarize_best_epoch_sat_metrics(csv_path, txt_file, clingo_ltn_comparison, disagreement_values, best_epoch):
    df = pd.read_csv(csv_path)

    if df.empty:
        print("CSV is empty")
        return

    matches = df[df["Epoch"] == best_epoch]

    if matches.empty:
        # Fall back to the closest saved epoch
        closest_idx = (df["Epoch"] - best_epoch).abs().idxmin()
        best = df.iloc[closest_idx]
        print(f"Epoch {best_epoch} not found; using closest: {best['Epoch']}")
    else:
        best = matches.iloc[0]

    # --- Core training info ---
    txt_file.write("\n========= Rule Satisfaction in LTNs =========\n")
    #txt_file.write("\n========= TODO: DISAGREEMENT VALUES =========\n")


    # --- Accuracy groups ---
    train_acc = {k.replace("_train_accuracy", ""): best[k]
                 for k in df.columns if k.endswith("_train_accuracy")}

    val_acc = {k.replace("_val_accuracy", ""): best[k]
               for k in df.columns if k.endswith("_val_accuracy")}

    
    #active_axioms = rules_and_concepts.get_active_axioms()

    txt_file.write("\nAxiom satisfaction: training\n\n")
    for k, v in sorted(train_acc.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")

    txt_file.write("\nAxiom satisfaction: validation \n\n")
    for k, v in sorted(val_acc.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")


    txt_file.write("\n" + "="*50)
    txt_file.write("\n========= LTN vs Clingo =========\n")

    txt_file.write("\n agreement per axiom \n\n")
    for k,v in sorted(val_acc.items(), key=lambda x: -x[1]):
        comparison = clingo_ltn_comparison.get(k, {})
        txt_file.write(f"{k:20s}: {comparison}\n")

    txt_file.write("\n\n Disagreements between LTN and CLINGO \n\n")
    for rule_name, sid_dict in disagreement_values.items():
        txt_file.write(f"\n\n\n--- {rule_name} ({len(sid_dict)} disagreements) ---\n")
        for sid, values in sid_dict.items():
            txt_file.write(f"  {sid}\n")
            txt_file.write(f"    ltn={values['ltn_binary']} clingo={values['clingo_binary']}"
                        f" body={values['final_result']:.4f}")
            
            if values['final_result'] > 0.6 or values['final_result'] < 0.4:
                txt_file.write("  PROBLEMATIC RESULT, check for weak antecedent pattern Reisenbarch\n")
            else:
                txt_file.write("\n")


            for cn, pv in values["concepts"].items():
                distance = abs(pv - 0.5)
                txt_file.write(f"    {cn:15s} = {pv:.4f}  (|d-0.5|={distance:.4f})\n")


def summarize_best_epoch(csv_path, txt_file, best_epoch):
    df = pd.read_csv(csv_path)

    if df.empty:
        print("CSV is empty")
        return

        # Find the row where the epoch column matches best_epoch
    matches = df[df["Epoch"] == best_epoch]

    if matches.empty:
        # Fall back to the closest saved epoch
        closest_idx = (df["Epoch"] - best_epoch).abs().idxmin()
        best = df.iloc[closest_idx]
        print(f"Epoch {best_epoch} not found; using closest: {best['Epoch']}")
    else:
        best = matches.iloc[0]

    

    txt_file.write("\n" + "="*50)
    txt_file.write(f"BEST EPOCH SUMMARY (Epoch {int(best['Epoch'])})")
    txt_file.write("="*50)

    # --- Core training info ---
    txt_file.write("\nTraining Info\n")
    txt_file.write(f"Alpha: {best['Alpha']:.4f}\n")
    txt_file.write(f"Classification Train Loss: {best['train_loss']:.4f}\n")
    txt_file.write(f"Classification Val Loss: {best['val_loss']:.4f}\n")
    txt_file.write(f"Combined Train Loss: {best['combined_train_loss']:.4f}\n")
    txt_file.write(f"Combined Val Loss: {best['combined_val_loss']:.4f}\n")

    # --- Logic consistency ---
    txt_file.write("\nLogical Consistency: 1- KB\n")
    best_train_sat = 1 - best['train_sat_kb']
    best_val_sat = 1-best['val_sat_kb']
    txt_file.write(f"Train SAT (Loss): {best_train_sat:.4f}\n")
    txt_file.write(f"Val SAT (Loss): {best_val_sat:.4f}\n")

    # --- Accuracy groups ---
    train_acc = {k.replace("_train_accuracy", ""): best[k]
                 for k in df.columns if k.endswith("_train_accuracy")}

    val_acc = {k.replace("_val_accuracy", ""): best[k]
               for k in df.columns if k.endswith("_val_accuracy")}

    
    final_classes = rules_and_concepts.get_normalized_FINAL_CLASSES()

    class_train_acc = {k: train_acc[k] for k in train_acc if k in final_classes}
    concept_train_acc = {k: train_acc[k] for k in train_acc if k not in final_classes}
    class_val_ac = {k: val_acc[k] for k in val_acc if k in final_classes}
    concept_val_acc = {k: val_acc[k] for k in val_acc if k not in final_classes}



    txt_file.write("\nTrain Accuracy per Class, final classes\n")
    for k, v in sorted(class_train_acc.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")

    txt_file.write("\nTrain Accuracy per Class, concepts\n")
    for k, v in sorted(concept_train_acc.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")

    txt_file.write("\nValidation Accuracy per Class, final classes\n")
    for k, v in sorted(class_val_ac.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")

    txt_file.write("\nValidation Accuracy per Class, concepts\n")
    for k, v in sorted(concept_val_acc.items(), key=lambda x: -x[1]):
        txt_file.write(f"{k:20s}: {v:.3f}\n")

    txt_file.write("\n" + "="*50)
    txt_file.write("\n\n")


    vac_counts = axioms.get_vac_counts()
    txt_file.write("\nVacuous Counts per Class, building classes\n")
    for cls, count in vac_counts.items():
        txt_file.write(f"  {cls:20s}: {count}\n")




def write_to_csv_file(template, csv_template, results, epoch, alpha, csv_file, csv_path):

    #metrics_results = [metrics.result() for metrics in metrics_dict.values()]
    print(template.format(epoch, *results))
    if csv_path is not None:
        #csv_file.write(csv_template.format(epoch, *metrics_results) + "\n")
        csv_file.write(csv_template.format(epoch, alpha, *results) + "\n")
        csv_file.flush()
