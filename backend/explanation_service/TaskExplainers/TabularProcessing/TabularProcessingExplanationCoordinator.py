import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import torchvision.models as models
from rest_framework import status
from interfaces.IModalityExplanationCoordinator import IModalityExplanationCoordinator
import pandas as pd
from utils.utils import get_task_explainer, get_model_dataset_idx
import joblib

class TabularProcessingExplanationCoordinator(IModalityExplanationCoordinator):
    def __init__(self):
        self.module_path = "TaskExplainers.TabularProcessing."
        self.dataset = None
        self.model = None
        self.label = None

    def load_model(self, model_path):
        model = joblib.load(model_path)
        return model

    def load_data(self, data_path):
        return pd.read_csv(data_path)

    def run_task_explainer(self, task, method, data_path):
        model_idx, dataset_idx = get_model_dataset_idx(data_path)
        if model_idx is not None:
            model_path = next(iter(model_idx.values()))
            self.model = self.load_model(model_path)
        else:
            return {"result": "Model not found. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        if dataset_idx is not None:
            dataset_path = next(iter(dataset_idx.values()))
            self.dataset = self.load_data(dataset_path)
        else:
            return {"result": "Dataset not found. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        method_explainer = get_task_explainer(self.module_path, task, method)
        result = method_explainer.explain(dataset=self.dataset, model=self.model, remains=data_path)
        return result