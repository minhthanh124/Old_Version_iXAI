from interfaces.IValidatorStrategy import IValidatorStrategy
from rest_framework import status
import torch
import torch.nn as nn
import os
import torchvision.transforms as transforms
from utils.utils import validate_label_file

def load_model(model):
    loaded_model = torch.load(model, weights_only=False, map_location=torch.device('cpu'))
    loaded_model.eval()
    return loaded_model

def get_conv_layer(model):
    for name, module in model.named_modules():
        if isinstance(module, nn.Conv2d):
            if not (name.startswith("classifier") or name.startswith("aux")):
                return {"message": "The uploaded model is valid", "status": status.HTTP_200_OK}
    return {"message": "No CNN architecture found in your uploaded model. Please upload another model", "status": status.HTTP_404_NOT_FOUND}

class ComputerVisionDataValidator(IValidatorStrategy):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComputerVisionDataValidator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.dataset_rules = ['.png', '.jpg', '.jpeg']
            self.model_rules   = ['.pth']
            self.label_rules   = ['.csv', '.xlsx']
            self._initialized = True

    def validate_data(self, file, data_type):
        if not isinstance(data_type, str) or not isinstance(file.name, str):
            return {"message": "Invalid format", "status": status.HTTP_400_BAD_REQUEST}
        match data_type:
            case "Dataset":
                if self.get_file_extension(file.name) in self.dataset_rules:
                    return {"message": "Valid", "status": status.HTTP_200_OK}                    
            case "Model":
                if self.get_file_extension(file.name) in self.model_rules:
                    model = load_model(file)
                    response = get_conv_layer(model)
                    if response.get("status") == status.HTTP_200_OK:
                        return {"message": "Valid", "status": status.HTTP_200_OK}
                    else:
                        return {"message": response.get("message"), "status": response.get("status")}
            case "Label":
                if self.get_file_extension(file.name) in self.label_rules:
                    response = validate_label_file(file)
                    if response.get("status") != 200:
                        return {"message": response.get("message"), "status": response.get("status")}
                    return {"message": "Valid", "status": status.HTTP_200_OK}
        return {"message": "The file is unsupported.", "status": status.HTTP_400_BAD_REQUEST}

    def get_file_extension(self, file_name):
        return os.path.splitext(file_name)[1]

