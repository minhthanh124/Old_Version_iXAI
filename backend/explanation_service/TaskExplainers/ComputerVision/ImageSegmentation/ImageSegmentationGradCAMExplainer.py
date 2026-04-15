
from interfaces.IGradcamExplainer import IGradcamExplainer
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import SemanticSegmentationTarget
import os
from io import BytesIO
import base64
from rest_framework import status
import torch.nn.functional as F
from utils.utils import extract_conv_layer, get_last_conv_layer, get_class_name, get_list_current_layers, format_target_class, get_target_list, generate_explanation_description
from pytorch_grad_cam.base_cam import BaseCAM

class SegmentationWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        output = self.model(x)
        if isinstance(output, dict):
            for key in ['out', 'logits']:
                if key in output:
                    output = output[key]
                    break
        return output

class ImageSegmentationGradCAMExplainer(IGradcamExplainer):
    def __init__(self):
        self.datatypes = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def pre_processing(self, dataset):
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
        ])
        input_tensor = transform(dataset).unsqueeze(0).to(self.device)
        return input_tensor

    def compute_cam(self, **kwargs):
        model = kwargs.get("model")
        wrapped_model = SegmentationWrapper(model)
        input_tensor = kwargs.get("input_tensor")
        target_layer = kwargs.get("target_layer")
        segmentation_output = kwargs.get("segmentation_output")
        target_class = kwargs.get("target_class")
        target_classes = None
        pred_mask = segmentation_output.squeeze(0).argmax(0).cpu().numpy()
        
        if target_class is None:
            unique_classes, counts = np.unique(pred_mask, return_counts=True)
            target_classes = [int(cls) for cls in unique_classes if cls != 0]  # filter out background class 0
            target_classes = target_classes[::-1]
            non_background = [(cls, cnt) for cls, cnt in zip(unique_classes, counts) if cls != 0]
            if not non_background:
                raise ValueError("No foreground classes detected in the prediction.")
            target_class = max(non_background, key=lambda x: x[1])[0] 
        
        cam = GradCAM(model=wrapped_model, target_layers=[target_layer])
        probs = F.softmax(segmentation_output, dim=1)
        predicted_mask = segmentation_output.argmax(dim=1)[0].cpu().numpy()
        target_pixels_mask = predicted_mask == target_class
        target_class_probs = probs[0, target_class].cpu().numpy()
        if np.any(target_pixels_mask):
            target_score = target_class_probs[target_pixels_mask].mean() * 100
        else:
            target_score = 0.0

        targets = [SemanticSegmentationTarget(category=target_class, mask=predicted_mask == target_class)]
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]
        return grayscale_cam, target_class, target_score, target_classes

    def apply_cam(self, **kwargs):
        image_pil = kwargs.get("image_pil")
        grayscale_cam = kwargs.get("grayscale_cam")
        target_class = kwargs.get("target_class")
        image_np = np.array(image_pil.resize((512, 512))) / 255.0
        cam_overlay = show_cam_on_image(image_np, grayscale_cam, use_rgb=True)
        fig, ax = plt.subplots()
        ax.imshow(cam_overlay)
        ax.axis('off')
        ax.set_title("Grad-CAM")
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        return buffer.read()

    def explain(self, **kwargs):
        target_class_name = None
        label_path = ""
        class_name = "Unknown"
        data_path = kwargs.get("remains")
        label_idx = next((pair[1] for pair in data_path if pair[0] == "label_path"), None)
        layer = next((pair[1] for pair in data_path if pair[0] == "layer"), None)
        object = next((pair[1] for pair in data_path if pair[0] == "object"), None)
        if label_idx is not None:
            label_path = next(iter(label_idx.values()))

        image_pil = kwargs.get("dataset").resize((512, 512))
        input_tensor = self.pre_processing(image_pil)
        model = kwargs.get("model")
        if isinstance(model, torch.nn.Module):
            model = model.to(self.device)
        model.eval()
        target_class = None
        if layer is not None:
            target_layer_name = layer
        else:
            target_layer_name = get_last_conv_layer(model)
        if object is not None:
            if str(object).isdigit():
                target_class = int(object)
            else:
                target_class = get_class_name(label_path, object, True)
        
        target_layer = model.get_submodule(target_layer_name)
        target_layer_name = f"{target_layer_name}: {target_layer}"

        with torch.no_grad():
            output = model(input_tensor)
            if isinstance(output, dict):
                for key in ['out', 'logits']:
                    if key in output:
                        output = output[key]
                        break
            segmentation_output = output
        grayscale_cam, target_class, target_score, target_classes = self.compute_cam(model=model, input_tensor=input_tensor, 
                                                                                    target_layer=target_layer, 
                                                                                    segmentation_output=segmentation_output, 
                                                                                    target_class=target_class)
        cam_image_bytes = self.apply_cam(image_pil=image_pil, grayscale_cam=grayscale_cam, target_class=target_class)
        cam_image_base64 = base64.b64encode(cam_image_bytes).decode('utf-8')
        score = f"{target_score:.2f}%"

        if label_path:
            class_name = get_class_name(label_path, target_class)
            target_class_name = get_target_list(label_path, target_classes)
        
        conv_layers = extract_conv_layer(model)
        list_cnn_layers = get_list_current_layers(conv_layers)

        # description = (
        #     f"Predicted Label: {class_name}\n"
        #     f"Score: {score}\n"
        #     f"The explanation is generated at layer: {target_layer_name}"
        # )
        if target_class_name is not None:
            extra_data = {"target_classes": target_class_name, 
                        "cnn_layer": list_cnn_layers}
        elif target_classes is not None:
            extra_data = {"target_classes": target_classes, 
            "cnn_layer": list_cnn_layers}
        else:
            extra_data = {}
        result = {"image_base64": cam_image_base64}
        
        # Generate simplified description using GPT
        gpt_description_initialize = ""
        gpt_description = generate_explanation_description(result, 'computer_vision', prediction=class_name)
        if gpt_description and not gpt_description.startswith("Unable to"):
            gpt_description_initialize = gpt_description

        description = (
            f"Predicted Label: {class_name}\n"
            f"Score: {score}\n"
           # f"The explanation is generated at layer: {target_layer_name}\n"
            f"Description: {gpt_description_initialize}"
        )
        
        return {"result": result, "description": description, "extra_data": extra_data, "status": status.HTTP_200_OK}