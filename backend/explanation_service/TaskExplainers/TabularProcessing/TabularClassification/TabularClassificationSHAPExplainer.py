import inspect
import shap
import numpy as np
from transformers import AutoTokenizer
from interfaces.IShapExplainer import IShapExplainer
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from rest_framework import status
from utils.utils import fix_html_shap_format, generate_explanation_description
import seaborn as sns
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import io
import base64
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class TabularClassificationSHAPExplainer(IShapExplainer):
    def __init__(self):
        self.model = None
        self.X_test = None
        self.description = ""
        self.extra_data = ""

    def pre_processing(self, dataset):
        X = dataset.drop('Class', axis=1)
        y = dataset['Class']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    def build_shap_explainer(self):
        explainer = shap.Explainer(self.model, self.X_test)
        return explainer

    def compute_shap_values(self, explainer, input_texts):
        shap_values = explainer(input_texts)
        return shap_values

    def explain(self, **kwargs):
        self.model = kwargs.get("model")
        dataset = kwargs.get("dataset")
        X_train, X_test, y_train, y_test = self.pre_processing(dataset)
        self.X_test = X_test
        explainer = self.build_shap_explainer()
        shap_values = self.compute_shap_values(explainer, X_test)
        fig, ax = plt.subplots(figsize=(3, 1))
        shap.plots.waterfall(shap_values[0], show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()
        result = {"plot_waterfall": img_base64}
        
        # Generate simplified description using the configured LLM provider
        llm_description = generate_explanation_description(result, 'tabular')
        if llm_description and not llm_description.startswith('AI-powered description unavailable'):
            self.description = llm_description
        
        return {"result": result, "description": self.description, "extra_data": self.extra_data, "status": status.HTTP_200_OK}