import torch

from utils import axioms
import dissertation_workplace_script as script

logits_model, device, classification_loss_fn, super_loss_fn, p = script.reset_model(in_channels=3, num_classes=12, seed=12345)


axioms.reset_rule_sat_metrics()
gt_sat_accumulator = []
for batch_elements_test in script.test_loader:
    features_param, labels_list = script.__get_elements_from_batch(batch_elements_test)
    labels_list = [lbl.to(device) for lbl in labels_list]

    SCALE = 8.0
    gt_tensor = torch.stack(labels_list, dim=1).float()
    pseudo_logits = gt_tensor * (2 * SCALE) - SCALE

    gt_sat = axioms.compute_axioms(pseudo_logits, *labels_list, p=p, debug_mode=False, validation_mode=True)
    gt_sat_accumulator.append(gt_sat.item())

true_baseline = sum(gt_sat_accumulator) / len(gt_sat_accumulator)
print(f"true unperturbed baseline: {true_baseline:.4f}")