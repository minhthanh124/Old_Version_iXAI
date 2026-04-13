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
import pandas as pd
from utils.utils import get_task_explainer, get_model_dataset_idx
from transformers import AutoTokenizer

class NaturalLanguageProcessingExplanationCoordinator(IModalityExplanationCoordinator):
    def __init__(self):
        self.module_path = "TaskExplainers.NaturalLanguageProcessing."
        self.dataset = None
        self.tokenizer = None
        self.model = None
        self.label = None

    def load_model(self, model_path):
        model = torch.load(model_path, weights_only=False)
        return model

    def load_data(self, data_path):
        encoding = "utf-8"
        content = ''
        with open(data_path, 'r', encoding=encoding) as f:
            content= f.read()
        if not content:
            return {
                "status": "error",
                "message": "Empty file"
            }
        return content

    def run_task_explainer(self, task, method, data_path):
        model_idx, dataset_idx = get_model_dataset_idx(data_path)
        tokenizer_idx = next((pair[1] for pair in data_path if pair[0] == "tokenizer_path"), None)

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
        if tokenizer_idx is not None:
            tokenizer_path = next(iter(tokenizer_idx.values()))
            self.tokenizer = self.load_tokenizer(tokenizer_path)
            if self.tokenizer is None:
                return {"result": "Invalid tokenizer. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        else:
            return {"result": "Tokenizer not found. Please upload again.", "description": "", "status": status.HTTP_404_NOT_FOUND}
        method_explainer = get_task_explainer(self.module_path, task, method)
        result = method_explainer.explain(dataset=self.dataset, model=self.model, tokenizer=self.tokenizer, remains=data_path)
        return result
    def load_tokenizer(self, tokenizer_path):
        try:
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            return tokenizer
        except Exception as e:
            return None
