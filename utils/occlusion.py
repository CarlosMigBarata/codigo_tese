import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def occlusion_map(model, image, class_idx, patch_size=20, stride=10, final_classes=1, device="cpu"):
    """
    image: tensor [3, H, W]
    class_idx: int (which class to analyze)
    """

    model.eval()

    image = image.to(device)
    _, H, W = image.shape

    heatmap = np.zeros((H, W))

    # Get original prediction
    with torch.no_grad():
        logits = model(image.unsqueeze(0))
        probs = torch.sigmoid(logits[:, :final_classes])

        #concepts = torch.sigmoid(logits[:, final_classes:])
        #score = concepts[0, concept_idx]

        baseline = probs[0, class_idx].item()

    # Slide occlusion patch
    for y in range(0, H, stride):
        for x in range(0, W, stride):
            occluded = image.clone()

            y1, y2 = y, min(y + patch_size, H)
            x1, x2 = x, min(x + patch_size, W)

            # Zero-out patch (you can also use mean color)
            occluded[:, y1:y2, x1:x2] = 0

            with torch.no_grad():
                logits = model(occluded.unsqueeze(0))
                probs = torch.sigmoid(logits[:, :final_classes])
                score = probs[0, class_idx].item()

            drop = baseline - score

            heatmap[y1:y2, x1:x2] += drop

    return heatmap

def show_occlusion(image, heatmap, save_folder, id):
    image = image.permute(1, 2, 0).cpu().numpy()

    output_dir = Path(f"{save_folder}/plots/images")
    output_dir.mkdir(exist_ok=True)

    save_path = output_dir / f"occlusion_map{id}.png"
    save_path_image = output_dir / f"base_image{id}.png"

    plt.imshow(image)
    plt.savefig(save_path_image)
    plt.imshow(heatmap, cmap="jet", alpha=0.5)
    plt.colorbar()
    plt.title("Occlusion Map")
    plt.axis("off")
    #plt.show()

    plt.savefig(save_path)
    plt.close()

'''
relevant classes é o conjunto de classes que o modelo está a usar para treinar
all classes é o conjunto de todas as classes presentes no dataset/ontologia
'''
def write_image_info(relevant_classes, all_classes, image_id, image_concepts, txt_path ):
    txt_file = open(txt_path, "w+")

    relevant_concepts_present = [
        relevant_classes[j]
        for j, val in enumerate(image_concepts)
        if val == 1
    ]

    print(f"relevant concepts: {relevant_concepts_present} ")
    txt_file.write(f"relevant concepts: {relevant_concepts_present} for image {image_id}\n")

    all_concepts_present = [
        all_classes[j]
        for j, val in enumerate(image_concepts)
        if val == 1
    ]

    print(f"all concepts: {all_concepts_present}")
    txt_file.write(f"relevant concepts: {all_concepts_present} for image {image_id}\n")