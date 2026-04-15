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
import json

class TextClassificationSHAPExplainer(IShapExplainer):
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.description = ""
        self.extra_data = ""
        self.label = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def pre_processing(self, dataset):
        return ""

    def build_shap_explainer(self):
        explainer = shap.Explainer(self.predict_fn, self.tokenizer)
        return explainer

    def compute_shap_values(self, explainer, input_texts):
        shap_values = explainer(input_texts)
        return shap_values

    def load_label(self, label_path):
        with open(label_path, 'r') as f:
            label_map = json.load(f)
        return label_map

    def explain(self, **kwargs):
        model = kwargs.get("model")
        tokenizer = kwargs.get("tokenizer")
        dataset = kwargs.get("dataset")
        data_path = kwargs.get("remains")
        label_idx = next((pair[1] for pair in data_path if pair[0] == "label_path"), None)
        if label_idx is not None:
            label_path = next(iter(label_idx.values()))
            self.label = self.load_label(label_path)
        input_texts = [dataset]
        if isinstance(model, torch.nn.Module):
            model = model.to(self.device)
        model.eval()
        model.config.is_decoder = True
        self.model = model
        self.tokenizer = tokenizer
        explainer = self.build_shap_explainer()
        shap_values = self.compute_shap_values(explainer, input_texts)
        if self.label is not None:
            shap_values.output_names = list(self.label.values())
        
        # Generate HTML visualization
        html_str = shap.plots.text(shap_values, display=False)
        html_str = fix_html_shap_format(html_str)
        
        # Create structured text representation for LLM
        text_explanation = self._create_text_explanation(shap_values, dataset)
        
        result = {"html_str": html_str, "text_explanation": text_explanation}
        result_for_explanation = {"text_explanation": text_explanation}
        
        # Generate simplified description using the configured LLM provider
        llm_description = generate_explanation_description(result_for_explanation, 'natural_language')
        if llm_description and not llm_description.startswith('AI-powered description unavailable'):
            self.description = llm_description

        return {"result": result, "description": self.description, "extra_data": self.extra_data, "status": status.HTTP_200_OK}

    def predict_fn(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        elif isinstance(texts, np.ndarray):
            texts = texts.tolist()
        tokenized = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        tokenized = {k: v.to(self.device) for k, v in tokenized.items()}
        with torch.no_grad():
            outputs = self.model(**tokenized)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().numpy()
        return probabilities

    def _create_text_explanation(self, shap_values, original_text):
        """Create a structured text representation of SHAP values for LLM understanding."""
        try:
            # Get the predicted class and its probability
            predictions = self.predict_fn(original_text)
            predicted_class_idx = np.argmax(predictions[0])
            predicted_prob = predictions[0][predicted_class_idx]
            
            # Get class name if available
            predicted_class = f"Class {predicted_class_idx}"
            if self.label and predicted_class_idx < len(self.label):
                predicted_class = list(self.label.values())[predicted_class_idx]
            
            explanation_parts = []
            explanation_parts.append(f"Original Text: '{original_text}'")
            explanation_parts.append(f"Predicted Class: {predicted_class} (confidence: {predicted_prob:.3f})")
            explanation_parts.append("")
            
            # Extract token-level SHAP values
            if hasattr(shap_values, 'values') and len(shap_values.values) > 0:
                token_shap = shap_values.values[0]  # First sample
                tokens = shap_values.data[0] if hasattr(shap_values, 'data') else []
                
                # For multi-class, get SHAP values for predicted class
                if len(token_shap.shape) > 1:
                    shap_for_predicted = token_shap[:, predicted_class_idx]
                else:
                    shap_for_predicted = token_shap
                
                # Create token importance list
                token_importance = []
                for i, (token, shap_val) in enumerate(zip(tokens, shap_for_predicted)):
                    token_importance.append((token, float(shap_val)))
                
                # Sort by absolute SHAP value (most important first)
                token_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
                explanation_parts.append("Token Importance (SHAP values):")
                for token, shap_val in token_importance[:20]:  # Top 20 most important
                    direction = "POSITIVE" if shap_val > 0 else "NEGATIVE"
                    explanation_parts.append(f"  '{token}': {shap_val:.4f} ({direction} contribution to {predicted_class})")
                
                explanation_parts.append("")
                explanation_parts.append("Most important tokens for this prediction:")
                positive_tokens = [(t, v) for t, v in token_importance if v > 0][:5]
                negative_tokens = [(t, v) for t, v in token_importance if v < 0][:5]
                
                if positive_tokens:
                    explanation_parts.append("Tokens that INCREASED likelihood of this prediction:")
                    for token, val in positive_tokens:
                        explanation_parts.append(f"  + '{token}' (impact: +{val:.4f})")
                
                if negative_tokens:
                    explanation_parts.append("Tokens that DECREASED likelihood of this prediction:")
                    for token, val in negative_tokens:
                        explanation_parts.append(f"  - '{token}' (impact: {val:.4f})")
            
            return "\n".join(explanation_parts)
            
        except Exception as e:
            return f"Error creating text explanation: {str(e)}"