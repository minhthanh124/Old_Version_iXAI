import inspect
import torch
import shap
import numpy as np
from transformers import AutoTokenizer
from interfaces.IShapExplainer import IShapExplainer
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from rest_framework import status
from utils.utils import fix_html_shap_format, generate_explanation_description

class QuestionAnsweringSHAPExplainer(IShapExplainer):
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.description = ""
        self.extra_data = ""
        self.MAX_LEN = 50
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def pre_processing(self, dataset):
        return dataset.replace("[SEP]", self.tokenizer.sep_token)

    def build_shap_explainer(self):
        explainer = shap.Explainer(self.f_end, self.tokenizer)
        return explainer

    def compute_shap_values(self, explainer, input_texts):
        shap_values = explainer(input_texts)
        return shap_values

    def explain(self, **kwargs):
        model = kwargs.get("model")
        tokenizer = kwargs.get("tokenizer")
        dataset = kwargs.get("dataset")
        if isinstance(model, torch.nn.Module):
            model = model.to(self.device)
        model.eval()
        model.config.is_decoder = True
        self.model = model
        self.tokenizer = tokenizer
        raw_input = self.pre_processing(dataset)
        input_texts = [raw_input]
        explainer = self.build_shap_explainer()
        shap_values = self.compute_shap_values(explainer, input_texts)
        shap_values.output_names = self.out_names(raw_input)
        
        # Generate HTML visualization
        html_str = shap.plots.text(shap_values, display=False)
        html_str = fix_html_shap_format(html_str)
        
        # Create structured text representation for LLM
        text_explanation = self._create_text_explanation(shap_values, raw_input)
        
        result = {"html_str": html_str, "text_explanation": text_explanation}
        result_for_explanation = {"text_explanation": text_explanation}
        
        # Generate simplified description using the configured LLM provider
        llm_description = generate_explanation_description(result_for_explanation, 'natural_language')
        if llm_description and not llm_description.startswith('AI-powered description unavailable'):
            self.description = llm_description

        return {"result": result, "description": self.description, "extra_data": self.extra_data, "status": status.HTTP_200_OK}

    def f(self, questions, start):
        out = []
        for pair in questions:
            question, context = pair.split(self.tokenizer.sep_token)
            tokenized = self.tokenizer(question.strip(), context.strip(), padding='max_length',truncation=True, max_length=self.MAX_LEN, return_tensors='pt')
            tokenized = {k: v.to(self.device) for k, v in tokenized.items()}
            output = self.model(**tokenized)
            logits = output.start_logits if start else output.end_logits
            out.append(logits.detach().cpu().numpy().flatten())
        return out

    # SHAP model functions
    def f_start(self, questions):
        return self.f(questions, True)

    def f_end(self, questions):
        return self.f(questions, False)

    # for labeling SHAP outputs
    def out_names(self, inputs):
        question, context = inputs.split(self.tokenizer.sep_token)
        d = self.tokenizer(question.strip(), context.strip(), padding='max_length', truncation=True, max_length=self.MAX_LEN)
        return [self.tokenizer.decode([id]) for id in d["input_ids"]]

    def _create_text_explanation(self, shap_values, raw_input):
        """Create a structured text representation of SHAP values for Q&A task."""
        try:
            question, context = raw_input.split(self.tokenizer.sep_token)
            question = question.strip()
            context = context.strip()
            
            # Tokenize to get input IDs and tokens
            tokenized = self.tokenizer(question, context, padding='max_length', truncation=True, max_length=self.MAX_LEN)
            input_ids = tokenized['input_ids']
            tokens = [self.tokenizer.decode([id]) for id in input_ids]
            
            # Get model predictions for start and end positions
            with torch.no_grad():
                model_output = self.model(
                    input_ids=torch.tensor([input_ids], device=self.device),
                    attention_mask=torch.tensor([tokenized['attention_mask']], device=self.device)
                )
                start_logits = model_output.start_logits[0].cpu().numpy()
                end_logits = model_output.end_logits[0].cpu().numpy()
            
            # Get predicted start and end positions
            pred_start_idx = np.argmax(start_logits)
            pred_end_idx = np.argmax(end_logits)
            
            # Extract predicted answer span
            answer_tokens = tokens[pred_start_idx:pred_end_idx + 1]
            predicted_answer = self.tokenizer.convert_tokens_to_string(
                [self.tokenizer.convert_ids_to_tokens(id) for id in input_ids[pred_start_idx:pred_end_idx + 1]]
            )
            
            explanation_parts = []
            explanation_parts.append(f"Question: '{question}'")
            explanation_parts.append(f"Context: '{context}'")
            explanation_parts.append(f"Predicted Answer: '{predicted_answer}'")
            explanation_parts.append(f"Answer Start Position: Token {pred_start_idx}, End Position: Token {pred_end_idx}")
            explanation_parts.append("")
            
            # Extract SHAP values for start and end positions
            if hasattr(shap_values, 'values') and len(shap_values.values) > 0:
                # Get SHAP values - they should be for end position since we used f_end
                shap_data = shap_values.values[0]  # First sample
                
                # Create token importance list
                token_importance = []
                for i, (token, shap_val) in enumerate(zip(tokens, shap_data)):
                    if token.strip():  # Skip empty tokens
                        token_importance.append((token, float(shap_val), i))
                
                # Sort by absolute SHAP value (most important first)
                token_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
                explanation_parts.append("Token Importance for Answer Prediction (SHAP values):")
                for token, shap_val, pos in token_importance[:15]:  # Top 15 most important tokens
                    direction = "POSITIVE" if shap_val > 0 else "NEGATIVE"
                    marker = "★" if pos >= pred_start_idx and pos <= pred_end_idx else ""
                    explanation_parts.append(f"  {marker} '{token}' (pos {pos}): {shap_val:.4f} ({direction})")
                
                explanation_parts.append("")
                explanation_parts.append("Tokens in predicted answer span:")
                for i in range(pred_start_idx, min(pred_end_idx + 1, len(tokens))):
                    explanation_parts.append(f"  [{i}] '{tokens[i]}'")
                
                # Most important tokens
                explanation_parts.append("")
                explanation_parts.append("Most influential tokens:")
                positive_tokens = [(t, v, p) for t, v, p in token_importance if v > 0][:5]
                negative_tokens = [(t, v, p) for t, v, p in token_importance if v < 0][:5]
                
                if positive_tokens:
                    explanation_parts.append("Tokens that INCREASED answer span confidence:")
                    for token, val, pos in positive_tokens:
                        explanation_parts.append(f"  + '{token}' at position {pos} (impact: +{val:.4f})")
                
                if negative_tokens:
                    explanation_parts.append("Tokens that DECREASED answer span confidence:")
                    for token, val, pos in negative_tokens:
                        explanation_parts.append(f"  - '{token}' at position {pos} (impact: {val:.4f})")
            
            return "\n".join(explanation_parts)
            
        except Exception as e:
            return f"Error creating text explanation: {str(e)}"