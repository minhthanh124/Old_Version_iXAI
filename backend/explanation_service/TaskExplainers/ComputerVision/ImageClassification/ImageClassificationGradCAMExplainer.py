import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import torchvision.models as models
from rest_framework import status
from PIL import Image
from interfaces.IGradcamExplainer import IGradcamExplainer
from io import BytesIO
import base64
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import pandas as pd
import torch.nn.functional as F

import logging

logger = logging.getLogger(__name__)


from utils.utils import extract_conv_layer, get_last_conv_layer, get_class_name, get_list_current_layers, format_target_class, get_target_list, generate_explanation_description

# Wrap model
class WrapperModel(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        if hasattr(self.model(x), "logits"):
            return self.model(x).logits
        else:
            return self.model(x)

class ImageClassificationGradCAMExplainer(IGradcamExplainer):
    def __init__(self):
        self.data_class = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def pre_processing(self, dataset):
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
        ])
        input_tensor = transform(dataset).unsqueeze(0).to(self.device)
        return input_tensor

    def compute_cam(self, **kwargs):
        model = kwargs.get("model")
        target_layer = kwargs.get("target_layer")
        input_tensor = kwargs.get("input_tensor")
        target_class = kwargs.get("target_class")
        cam = GradCAM(model=model, target_layers=[target_layer])
        targets = [ClassifierOutputTarget(target_class)] if target_class is not None else None
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]
        return grayscale_cam

    def apply_cam(self, **kwargs):
        image_pil = kwargs.get("image_pil")
        grayscale_cam = kwargs.get("grayscale_cam")
        image_np = np.array(image_pil.resize((224, 224))) / 255.0
        cam_image = show_cam_on_image(image_np, grayscale_cam, use_rgb=True)
        fig, ax = plt.subplots()
        ax.imshow(cam_image)
        ax.axis('off')
        ax.set_title("Grad-CAM")
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        return buffer.read()

    def get_target_class(self, model, input_tensor):
        try:
            with torch.no_grad():
                output = model(input_tensor)
                if isinstance(output, torch.Tensor):
                    probs = F.softmax(output, dim=1)
                    target_class = output.argmax().item()
                elif hasattr(output, "logits"):
                    logits = output.logits
                    probs = F.softmax(logits, dim=1)
                    target_class = logits.argmax(dim=-1)
            return target_class, probs
        except Exception as e:
            return None, None

    def explain(self, **kwargs):
        target_class_name = None
        label_path = ""
        class_name = "Unknown"
        image_pil = kwargs.get("dataset")
        input_tensor = self.pre_processing(image_pil)
        model = kwargs.get("model")
        if isinstance(model, torch.nn.Module):
            model = model.to(self.device)
            model.eval()
        data_path = kwargs.get("remains")
        label_idx = next((pair[1] for pair in data_path if pair[0] == "label_path"), None)
        layer = next((pair[1] for pair in data_path if pair[0] == "layer"), None)
        object = next((pair[1] for pair in data_path if pair[0] == "object"), None)
        if label_idx is not None:
            label_path = next(iter(label_idx.values()))

        if layer is not None:
            target_layer_name = layer
        else:
            target_layer_name = get_last_conv_layer(model)

        if object is not None:
            if str(object).isdigit():
                target_class = int(object)
            else:
                target_class = get_class_name(label_path, object, True)
        else:
            target_class, probs = self.get_target_class(model, input_tensor)
            if target_class is not None and probs is not None:
                target_class = format_target_class(target_class)
            else:
                return {"result": "Could not generate model output. Please check your model again.", "description": "", "extra_data": "", "status": status.HTTP_400_BAD_REQUEST}

        if label_path:
            class_name = get_class_name(label_path, target_class)
            target_class_name = get_target_list(label_path, target_class)
        
        target_layer = model.get_submodule(target_layer_name)
        target_layer_name = f"{target_layer_name}: {target_layer}"

        target_score = probs[0, target_class].item() * 100
        score = f"{target_score:.2f}%"
        wrapped_model = WrapperModel(model)
        grayscale_cam = self.compute_cam(model=wrapped_model, input_tensor=input_tensor, target_layer=target_layer, target_class=target_class)
        cam_image_bytes = self.apply_cam(image_pil=image_pil, grayscale_cam=grayscale_cam)
        cam_image_base64 = base64.b64encode(cam_image_bytes).decode('utf-8')
        conv_layers = extract_conv_layer(model)
        list_cnn_layers = get_list_current_layers(conv_layers)

        if target_class_name is not None:
            extra_data = {"target_classes": [target_class_name], 
                        "cnn_layer": list_cnn_layers}
        elif target_class is not None:
            extra_data = {"target_classes": [target_class], 
            "cnn_layer": list_cnn_layers}
        else:
            extra_data = {}
        result = {"image_base64": cam_image_base64}

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
        
        # Generate simplified description using the configured LLM provider
        # llm_description = generate_explanation_description(result, 'computer_vision')
        # if llm_description and not llm_description.startswith('AI-powered description unavailable'):
        #     description = llm_description

        return {"result": result, "description": description, "extra_data": extra_data, "status": status.HTTP_200_OK}
