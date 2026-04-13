import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import torchvision.models as models
from rest_framework import status
from PIL import Image
from interfaces.IModalityExplanationCoordinator import IModalityExplanationCoordinator
from io import BytesIO
import base64
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import pandas as pd
import torch.nn.functional as F
from utils.utils import get_task_explainer, get_model_dataset_idx

class ComputerVisionExplanationCoordinator(IModalityExplanationCoordinator):
    def __init__(self):
        self.module_path = "TaskExplainers.ComputerVision."

    def load_model(self, model_path):
        model = torch.load(model_path, weights_only=False)
        return model

    def load_data(self, data_path):
        raw_image = Image.open(data_path).convert('RGB')
        return raw_image

    def run_task_explainer(self, task, method, data_path):
        model_idx, dataset_idx = get_model_dataset_idx(data_path)
        if model_idx is not None:
            model_path = next(iter(model_idx.values()))
            model = self.load_model(model_path)
        else:
            return {"result": "Model not found. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        if dataset_idx is not None:
            dataset_path = next(iter(dataset_idx.values()))
            dataset = self.load_data(dataset_path)
        else:
            return {"result": "Dataset not found. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        method_explainer = get_task_explainer(self.module_path, task, method)
        result = method_explainer.explain(dataset=dataset, model=model, remains=data_path)
        return result


