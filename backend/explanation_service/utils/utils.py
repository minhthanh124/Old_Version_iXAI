import requests
import importlib
from rest_framework import status
import re
import pandas as pd
import torch
import torch.nn as nn
import os
from openai import OpenAI

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

pattern = r'(rgb|rgba)\(\s*np\.float64\(([\d\.]+)\)\s*,\s*np\.float64\(([\d\.]+)\)\s*,\s*np\.float64\(([\d\.]+)\)(?:\s*,\s*np\.float64\(([\d\.]+)\))?\s*\)'

def get_task_explainer(module_path, task, method):
    task_path = task.replace(" ", "")
    class_path = task_path + method + "Explainer"
    module_path = module_path + task_path +"."+ class_path
    module = importlib.import_module(module_path)
    explainer_class = getattr(module, class_path)
    explainer = explainer_class()
    return explainer

def replace_float64_color(match):
    color_type = match.group(1)
    r, g, b = match.group(2), match.group(3), match.group(4)
    a = match.group(5)
    if color_type == "rgba":
        return f"rgba({r}, {g}, {b}, {a})"
    else:
        return f"rgb({r}, {g}, {b})"

def fix_html_shap_format(html_str):
    return re.sub(pattern, replace_float64_color, html_str)

def extract_conv_layer(model):
    conv_layers = []
    for name, module in model.named_modules():
        if "classifier" not in name and "aux" not in name:
            if isinstance(module, nn.Conv2d):
                conv_layers.append((name, module))

    if not conv_layers:
        raise ValueError("No suitable Conv2D layers found before classifier/aux.")
    return conv_layers

def get_last_conv_layer(model):
    conv_layers = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Conv2d):
            if "classifier" not in name and "aux" not in name:
                conv_layers.append((name))
    if not conv_layers:
        raise ValueError("No suitable Conv2D layers found before classifier/aux.")
    return conv_layers[-1]

def get_class_name(label_path, class_id, get_index=False):
    df = pd.read_excel(label_path)
    if not get_index:
        label = df.loc[df['Index'] == class_id, 'Name']
    else:
        label = df.loc[df['Name'] == class_id, 'Index']
    if label.empty:
        return "Unknown"
    else:
        return label.iloc[0]

def get_target_list(label_path, target_class):
    target_list = []
    df = pd.read_excel(label_path)
    if not isinstance(target_class, list):
        target_class = [target_class]
    for target in target_class:
        label_name = df.loc[df['Index'] == target, 'Name']
        if label_name.empty:
            label_name = "Unknown"
        target_list.append(label_name)
    return target_list

def get_list_current_layers(conv_layers):
    tmp = ''
    init_layer = [conv_layers[0]]
    cnn_layers = []
    for item in conv_layers:
        rm_parent = '.'.join(item[0].split('.')[1:])
        if rm_parent.split(".")[0] != tmp:
            cnn_layers.append(init_layer[-1])
            tmp = rm_parent.split(".")[0]
        init_layer.append(item[0])
    cnn_layers.append(init_layer[-1])
    cnn_layers = cnn_layers[1:]
    cnn_layers = cnn_layers[::-1]
    return cnn_layers

def format_target_class(target_class):
    if hasattr(target_class, 'item'):
        predicted_class = target_class.item()
    elif isinstance(target_class, (list, tuple)):
        first = target_class[0]
        predicted_class = first.item() if hasattr(first, 'item') else int(first)
    else:
        predicted_class = int(target_class)
    return predicted_class

def get_model_dataset_idx(data_path):
    model_idx = next((pair[1] for pair in data_path if pair[0] == "model_path"), None)
    dataset_idx = next((pair[1] for pair in data_path if pair[0] == "dataset_path"), None)
    return model_idx, dataset_idx

def generate_explanation_description(explanation_result, modality_type, prediction="None"):
    """
    Generate a user-friendly description using Claude 3 Vision or GPT-4V for explanation results.
    
    Args:
        explanation_result: The result dictionary from the explainer
        modality_type: 'computer_vision', 'natural_language_processing', or 'tabular_processing'
        prediction: The predicted class/value as string
    
    Returns:
        str: Simplified description for non-experts
    """
    try:
        # Normalize modality type
        modality_type = modality_type.lower().replace(" ", "_")
        
        # Determine which provider to use
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        # For computer vision, send the actual image
        if modality_type == 'computer_vision':
            image_base64 = explanation_result.get('image_base64')
            if not image_base64:
                return "No image data available for explanation."
            
            if provider == 'claude' and Anthropic:
                return _generate_with_claude_vision(image_base64, prediction)
            else:
                return _generate_with_gpt4v(image_base64, prediction)
        
        # For NLP and Tabular, send text/HTML/plot description
        elif modality_type in ['natural_language_processing', 'natural_language']:
            # Prefer structured text explanation over raw HTML
            explanation_text = explanation_result.get('text_explanation') # or explanation_result.get('html_str', '')
            # if provider == 'claude' and Anthropic:
            #     return _generate_with_claude_text(explanation_text, 'natural_language', prediction)
            # else:
            return _generate_with_gpt(explanation_text, 'natural_language', prediction)
        
        elif modality_type in ['tabular_processing', 'tabular']:
            plot_desc = explanation_result.get('plot_waterfall', '')
            if provider == 'claude' and Anthropic:
                return _generate_with_claude_text(plot_desc, 'tabular', prediction)
            else:
                return _generate_with_gpt(plot_desc, 'tabular', prediction)
        
        else:
            result_description = str(explanation_result)[:500]
            if provider == 'claude' and Anthropic:
                return _generate_with_claude_text(result_description, 'general', prediction)
            else:
                return _generate_with_gpt(result_description, 'general', prediction)
    
    except Exception as e:
        return f"Unable to generate simplified description: {str(e)}"


def _generate_with_claude_vision(image_base64, prediction):
    """Generate description using Claude 3 Vision with actual image."""
    try:
        if not Anthropic:
            return "Anthropic SDK not installed. Install with: pip install anthropic"
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return "Claude API key not configured. Unable to generate simplified description."
        
        client = Anthropic(api_key=api_key)
        
        prompt = f"""You are an AI explanation expert. I'm showing you a Grad-CAM visualization of an image that the model predicted as: {prediction}.

The highlighted regions (especially red and yellow areas) in this image show which parts of the original image the AI model focused on to make its prediction.

Please generate a clear, simple description that non-expert users can easily understand:
1. What did the AI focus on in the image? (describe the highlighted regions)
2. How does this relate to the prediction of '{prediction}'?
3. Why do you think the AI made this prediction based on what it highlighted?

Use everyday language and avoid technical terms. Keep it to 3-4 sentences maximum."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text.strip()
    
    except Exception as e:
        return f"Claude Vision error: {str(e)}"


def _generate_with_gpt4v(image_base64, prediction):
    """Generate description using GPT-4 Vision with actual image."""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API key not configured. Unable to generate simplified description."
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""You are an AI explanation expert. I'm showing you a Grad-CAM visualization of an image that the model predicted as: {prediction}.

The highlighted regions (especially red and yellow areas) in this image show which parts of the original image the AI model focused on to make its prediction.

Please generate a clear, simple description that non-expert users can easily understand:
1. What did the AI focus on in the image? (describe the highlighted regions)
2. How does this relate to the prediction of '{prediction}'?
3. Why do you think the AI made this prediction based on what it highlighted?

Use everyday language and avoid technical terms. Keep it to 3-4 sentences maximum."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
            max_tokens=300,
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"GPT-4V error: {str(e)}"


def _generate_with_claude_text(text_data, data_type, prediction):
    """Generate description using Claude 3 for text/tabular data."""
    try:
        if not Anthropic:
            return "Anthropic SDK not installed. Install with: pip install anthropic"
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return "Claude API key not configured."
        
        client = Anthropic(api_key=api_key)
        
        if data_type == 'natural_language':
            prompt = f"""The model made prediction: {prediction}

Here is a structured SHAP explanation analysis:

{text_data}

This analysis shows which words/tokens were most important for the model's prediction. SHAP values indicate how much each token contributed to the final prediction (positive = increased likelihood, negative = decreased likelihood).

Please explain in simple terms what this SHAP analysis shows about why the model made this prediction. What words or phrases were most important and how did they influence the prediction? Keep it to 3-4 sentences."""
        
        elif data_type == 'tabular':
            prompt = f"""The model made prediction: {prediction}

Here is a SHAP waterfall plot explanation: {text_data[:1000]}

Please explain in simple terms what this shows about which features influenced the prediction most. Keep it to 3-4 sentences."""
        
        else:
            prompt = f"Explain this AI explanation result simply for non-experts (prediction: {prediction}): {text_data[:500]}"
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        
        return message.content[0].text.strip()
    
    except Exception as e:
        return f"Claude error: {str(e)}"


def _generate_with_gpt(text_data, data_type, prediction):
    """Generate description using GPT-4 for text/tabular data."""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API key not configured."
        
        client = OpenAI(api_key=api_key)
        
        if data_type == 'natural_language':
            prompt = f"""
Here is a structured SHAP explanation analysis:
{text_data}
This analysis shows which words/tokens were most important for the model's prediction. SHAP values indicate how much each token contributed to the final prediction (positive = increased likelihood, negative = decreased likelihood).
Please explain in simple terms what this SHAP analysis shows about why the model made this prediction. What words or phrases were most important and how did they influence the prediction? Keep it to 3-4 sentences."""
        
        elif data_type == 'tabular':
            prompt = f"""The model made prediction: {prediction}

Here is a SHAP waterfall plot explanation: {text_data[:1000]}

Please explain in simple terms what this shows about which features influenced the prediction most. Keep it to 3-4 sentences."""
        
        else:
            prompt = f"Explain this AI explanation result simply for non-experts (prediction: {prediction}): {text_data[:500]}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"GPT error: {str(e)}"
